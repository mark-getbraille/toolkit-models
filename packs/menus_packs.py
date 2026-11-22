"""Picture packs of RESTAURANT MENUS (the owner's request of 2026-11-22: pictures for the picture describer). Used by
build_packs.py in the same way as its own PACKS: build_<key>(limit) returns [(file name, JPEG bytes or None, row)]; a
picture with more than one question comes once with its JPEG and then as (None, None, row) rows naming the same
picture (food_packs.with_twins). The limit counts pictures.

Why: a printed menu is one of the commonest things a blind person cannot read, in a restaurant, a hotel or a
take-away bag. The describer should read a menu IN ORDER, with its dishes and prices, and say which restaurant it is
from.

The packs (MENUS_PACKS):
  nypl_menus       The New York Public Library's "What's on the Menu?" collection: about 17,500 historical menus
                   (1840s to 2000s, most 1890 to 1920) whose dishes and prices were transcribed by volunteers. The
                   data comes from the library's own published data dump (Menu, MenuPage, MenuItem and Dish CSV files,
                   in the bucket menusdata.nypl.org on Amazon S3, the newest dump, of March 2023; NYPL released the data
                   under CC0 1.0 on the project's data page, menus.nypl.org/data; that site has since been retired
                   (it now forwards to https://www.nypl.org/research/support/whats-on-the-menu), so the page itself
                   could not be read again on 2026-11-22) and each page's picture from images.nypl.org, NYPL's own picture server (its robots.txt is
                   absent, so nothing is disallowed), one at a time.
                   COPYRIGHT OF THE PICTURES: a menu is used only when
                     - its catalogue date is before 1931: published in or before 1930, it is in the public domain in
                       the United States (17 U.S.C. 304; works published before 1931 are out of copyright in 2026); or
                     - NYPL_API_TOKEN is set (a free token from https://api.repo.nypl.org, kept in the environment,
                       NEVER in this repository) and the library's Digital Collections API says for the page's capture
                       (GET /api/v2/items/rights/<uuid>) "No Known U.S. Copyright Restrictions" or CC0.
                   Menus without a date, or later than 1930 without that statement, are left out (considered-*.jsonl
                   says why). Every answer says only what the library's records say:
                     "What does this menu say?"        the dishes and prices transcribed for THAT page, in reading
                                                       order (top to bottom, then left to right, from the positions
                                                       the volunteers marked), prices as recorded with the menu's own
                                                       currency (no currency recorded: the number as recorded);
                     "What restaurant is this menu from?"  the place, sponsor, event, occasion and date of the record;
                     "What does the menu look like?"   on its first page only: the cataloguer's own physical
                                                       description and notes ("card; illustrated; colour ...");
                     "How much is <dish>?"             one dish with a recorded price, from the same page.
                   The volunteers transcribed dishes, not section headings, decorations or small print, and the
                   answers say "as transcribed" so they never claim more.
  synthetic_menus  Modern menus drawn here with Pillow from a fixed seed (SEED): made-up restaurants, addresses,
                   ".example" web sites and 555-01xx phone numbers, in common layouts: one column with sections,
                   two columns, a menu with small drawn pictures of dishes (each labelled, and described as a
                   drawing), a café price board, and a chalk "specials" board; dishes marked V (vegetarian), VG (vegan)
                   or GF (gluten-free) with the key printed; about half "photographed" by phone_photo.py. Every answer
                   is exact (the generator drew it): the whole menu in reading order, the restaurant's details, a
                   price, the vegetarian or gluten-free dishes, and the specials. Allergy answers end with ALLERGY_NOTE.

Not repeated: the Open Images "Menu" label (open_images_cards_documents, which says only that it is a menu) and the
NYPL photo pack (archive_packs.py), which leaves menus out.

    python packs/menus_packs.py synthetic_menus --limit 8 --save some-folder      (a quick check)
    python packs/menus_packs.py nypl_menus --limit 4
"""

import csv
import io
import os
import re
import sys
import tarfile
import tempfile

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import considered, pass_random, say, session
from phone_photo import font, phone_photo
from synthetic_documents import seeded

# ----------------------------------------------------------------- NYPL "What's on the Menu?"

DUMP_BUCKET = "https://s3.amazonaws.com/menusdata.nypl.org/"
DUMP_LIST = DUMP_BUCKET + "?list-type=2&prefix=gzips/"
PAGE_PICTURE = "https://images.nypl.org/index.php?id={image_id}&t=q"     # the library's 1,600-pixel copy
RIGHTS_API = "https://api.repo.nypl.org/api/v2/items/rights/{uuid}"
RECORD_PAGE = "https://digitalcollections.nypl.org/items/{uuid}"
OPEN_RIGHTS = re.compile(r"no known u\.?s\.? copyright|creativecommons\.org/publicdomain/zero|\bCC0\b", re.I)
READ_Q = "What does this menu say?"
FROM_Q = "What restaurant is this menu from?"
LOOK_Q = "What does the menu look like?"
MOST_ITEMS = 40               # dishes read out at most (then "and N more")
LEAST_ITEMS = 3               # a page with fewer transcribed dishes is left out
NYPL_CREDIT = ("From The New York Public Library, \"What's on the Menu?\" ({where}): menu data CC0 (NYPL), page "
               "picture {basis}. {page}")
NOT_GIVEN = re.compile(r"not given|unknown|^\W*$", re.I)


def latest_dump(s):
    """The address of the newest data dump in the library's bucket."""
    keys = re.findall(r"<Key>(gzips/[^<]+_data\.tgz)</Key>", s.get(DUMP_LIST, timeout=60).text)
    if not keys:
        raise RuntimeError("the NYPL menus data dump was not found")
    return DUMP_BUCKET + sorted(keys)[-1]


def read_dump(path):
    """{name: csv text} of the four CSV files in the dump at path (the big MenuItem file is read as a stream later)."""
    out = {}
    with tarfile.open(path, "r:gz") as tar:
        for member in tar.getmembers():
            base = os.path.basename(member.name)
            if base in ("Menu.csv", "MenuPage.csv", "MenuItem.csv", "Dish.csv") and member.isfile():
                out[base] = tar.extractfile(member).read().decode("utf-8", "replace")
    return out


def year_of(date):
    """The year of a record's date ("1900-04-15" -> 1900), or None."""
    found = re.match(r"(\d{4})", date or "")
    return int(found.group(1)) if found else None


def tidy(text):
    """A catalogue field made readable: brackets and trailing semicolons dropped, ALL-CAPS words in title case."""
    text = re.sub(r"[\[\]]", "", text or "").strip(" ;,")
    text = re.sub(r"\s*;\s*", "; ", text)
    return text.title() if text.isupper() else text


def price_words(price, currency, symbol):
    """A recorded price in words for the menu's currency ("$0.40", "40 cents", "2.5 Francs", or the number)."""
    if not price:
        return ""
    value = float(price)
    if currency == "Dollars":
        return f"${value:,.2f}"
    if currency == "Cents":
        return f"{value:g} cents"
    if currency:
        return f"{value:g} {currency}"
    return f"{value:g} (as recorded; no currency given)"


def long_date(date):
    """ "1900-04-15" as "April 15, 1900" (a year alone as the year)."""
    import datetime
    try:
        return datetime.date.fromisoformat(date).strftime("%B %-d, %Y")
    except (ValueError, TypeError):
        return str(year_of(date) or "")


def from_answer(menu):
    """ "It is from Hotel Eastman, Hot Springs, AR, a breakfast menu for Easter, dated April 15, 1900 (from the
    library's catalogue record)."."""
    place = next((tidy(menu.get(k)) for k in ("location", "sponsor", "name") if menu.get(k) and
                  not NOT_GIVEN.search(menu.get(k))), "")
    where = tidy(menu.get("place"))
    event, occasion = tidy(menu.get("event")).lower(), tidy(menu.get("occasion"))
    bits = [f"It is from {place}" if place else "The record does not name the restaurant"]
    if where:
        bits[0] += f", {where}"
    if event:
        bits.append(f"a {event} menu" + (f" for {occasion}" if occasion else ""))
    elif occasion:
        bits.append(f"for {occasion}")
    if menu.get("notes") and not menu.get("event") and len(menu["notes"]) < 120:
        bits.append(tidy(menu["notes"]).rstrip("."))
    if menu.get("date"):
        bits.append(f"dated {long_date(menu['date'])}")
    return ", ".join(bits) + " (from the New York Public Library's catalogue record)."


def read_answer(items, menu):
    """The page's transcribed dishes in reading order with their prices (see the module docstring)."""
    said = []
    for item in items[:MOST_ITEMS]:
        price = price_words(item["price"], menu.get("currency"), menu.get("currency_symbol"))
        said.append(item["dish"] + (f", {price}" if price else ""))
    more = len(items) - MOST_ITEMS
    tail = f"; and {more} more" if more > 0 else ""
    return ("As transcribed by volunteers for the New York Public Library, this page lists, from top to bottom: " +
            "; ".join(said) + tail + ".")


def look_answer(menu):
    """The cataloguer's physical description and notes, or "" when there are none."""
    parts = []
    if menu.get("physical_description"):
        words = tidy(menu["physical_description"]).lower()
        for short, full in (("illus", "illustrated"), ("col", "colour"), ("broadside", "broadside")):
            words = re.sub(rf"\b{short}\b\.?", full, words)
        parts.append(f"The library's catalogue describes it as: {words}")
    if menu.get("notes") and (menu.get("event") or len(menu["notes"]) >= 120):
        parts.append(f"Its notes say: {tidy(menu['notes']).lower()}")
    return ". ".join(parts) + "." if parts else ""


def page_rows(menu, page, items, credit):
    """The rows of one menu page (see the module docstring)."""
    rows = [{"question": READ_Q, "answer": read_answer(items, menu)}, {"question": FROM_Q, "answer": from_answer(menu)}]
    if str(page.get("page_number")) == "1" and look_answer(menu):
        rows.append({"question": LOOK_Q, "answer": look_answer(menu)})
    priced = [i for i in items if i["price"]]
    if priced:
        pick = priced[int(page["id"]) % len(priced)]
        rows.append({"question": f"How much is the {pick['dish']}?", "answer": f"It is listed at "
                     f"{price_words(pick['price'], menu.get('currency'), menu.get('currency_symbol'))} "
                     "(as transcribed)."})
    return [dict(r, credit=credit) for r in rows]


def rights_ok(s, uuid, token):
    """True when NYPL's Digital Collections API says the capture has no known US copyright restrictions or is CC0."""
    try:
        r = s.get(RIGHTS_API.format(uuid=uuid), timeout=60, headers={"Authorization": f'Token token="{token}"'})
        return r.status_code == 200 and bool(OPEN_RIGHTS.search(r.text))
    except Exception:  # noqa: BLE001 - no answer: not used
        return False


def menu_pages(files, limit, token=""):
    """[(menu, page, [items in reading order])] for pages that may be used (see the module docstring), shuffled in a
    fixed order, at most limit * 1.3; the reasons the others were left out go to considered()."""
    menus = {r["id"]: r for r in csv.DictReader(io.StringIO(files["Menu.csv"]))}
    pages = {r["id"]: r for r in csv.DictReader(io.StringIO(files["MenuPage.csv"]))}
    dishes = {}
    by_page = {}
    for item in csv.DictReader(io.StringIO(files["MenuItem.csv"])):
        if item["menu_page_id"] in pages and item.get("dish_id"):
            by_page.setdefault(item["menu_page_id"], []).append(item)
    for dish in csv.DictReader(io.StringIO(files["Dish.csv"])):
        dishes[dish["id"]] = dish["name"]
    out = []
    for page_id, items in by_page.items():
        page = pages[page_id]
        menu = menus.get(page["menu_id"])
        if not menu or not page.get("image_id"):
            continue
        named = []
        for item in items:
            name = re.sub(r"\s+", " ", dishes.get(item["dish_id"], "")).strip().rstrip(".;, ")
            try:
                y, x = float(item["ypos"] or 0), float(item["xpos"] or 0)
            except ValueError:
                y = x = 0.0
            if name:
                named.append({"dish": name, "price": item["price"], "y": y, "x": x})
        if len(named) < LEAST_ITEMS:
            continue
        named.sort(key=lambda i: (round(i["y"] * 40), i["x"]))      # rows about 1/40 of the page high, then across
        out.append((menu, page, named))
    pass_random("nypl-menus").shuffle(out)
    s, kept = session(), []
    for menu, page, named in out:
        if len(kept) >= limit * 1.3:
            break
        year = year_of(menu.get("date"))
        url = PAGE_PICTURE.format(image_id=page["image_id"])
        if year and year < 1931:
            kept.append((menu, page, named, f"published in {year}: public domain in the United States"))
        elif token and page.get("uuid") and rights_ok(s, page["uuid"], token):
            kept.append((menu, page, named, "\"No Known U.S. Copyright Restrictions\" or CC0 by NYPL's rights "
                                            "statement"))
        else:
            considered(f"nypl-menu-{page['id']}.jpg", url, "no date before 1931 and no open rights statement from "
                                                           "NYPL" if not token else "dated 1931 or later and NYPL's "
                                                                                   "rights statement is not open")
    return kept


def build_nypl_menus(limit):
    """The nypl_menus pack (see the module docstring)."""
    from food_packs import with_twins
    s = session()
    url = latest_dump(s)
    say(f"NYPL menus: reading {url}")
    folder = tempfile.mkdtemp(prefix="menus-")
    try:
        path = os.path.join(folder, "data.tgz")
        with s.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
        files = read_dump(path)
    finally:
        import shutil
        shutil.rmtree(folder, ignore_errors=True)
    token = os.environ.get("NYPL_API_TOKEN", "").strip()
    chosen = menu_pages(files, limit, token)
    say(f"NYPL menus: {len(chosen)} pages may be used" + ("" if token else " (no NYPL_API_TOKEN: only menus "
                                                                           "dated before 1931)"))
    items = []
    for menu, page, named, basis in chosen:
        where = RECORD_PAGE.format(uuid=page["uuid"]) if page.get("uuid") else "https://www.nypl.org"
        credit = NYPL_CREDIT.format(where=where, basis=basis, page=f"Menu {menu['id']}, page {page['page_number']}.")
        items.append((f"nypl-menu-{page['id']}.jpg", PAGE_PICTURE.format(image_id=page["image_id"]),
                      page_rows(menu, page, named, credit)))
    got = build_packs.fetch_all(items, workers=1, pause=1.0)
    return with_twins(got[:limit])


# ----------------------------------------------------------------- synthetic modern menus

SEED = 8807
CREDIT = ("A computer-made menu drawn with Pillow by packs/menus_packs.py (synthetic: made-up restaurant, address, "
          "web site under .example and 555-01xx phone number; not a real menu), CC0")
ALLERGY_NOTE = ("Menus can be wrong or change: if you have a food allergy, ask the staff before you order.")
RESTAURANTS = ("The Copper Kettle", "Blue Heron Bistro", "Saffron Lane", "Maple & Rye Diner", "Harbor Light Grill",
               "Little Fig Cafe", "Golden Lotus Kitchen", "Rosa's Cantina", "The Green Table", "Northside Pizza Co.",
               "Ember & Oak", "Pho Saigon Corner", "Olive Grove Taverna", "Sunrise Bakery Cafe")
STREETS = ("Main Street", "Harbor Road", "Elm Avenue", "Market Square", "Riverside Drive", "Oak Lane")
TOWNS = ("Clearwater Falls", "Port Ambry", "Lake Elsin", "Dunmore Springs", "Redstone Hollow")
SECTIONS = {
    "Starters": [("Soup of the Day", "Ask your server", ""), ("Garlic Bread", "Toasted with herb butter", "V"),
                 ("Crispy Calamari", "With lemon aioli", ""), ("Hummus Plate", "Warm pita, olives", "VG"),
                 ("Chicken Wings", "Buffalo or honey garlic", "GF"), ("Bruschetta", "Tomato, basil, garlic", "V"),
                 ("Spring Rolls", "Vegetable, sweet chili sauce", "VG"), ("Shrimp Cocktail", "Cocktail sauce", "GF")],
    "Salads": [("Caesar Salad", "Romaine, parmesan, croutons", ""), ("Greek Salad", "Feta, olives, cucumber", "V GF"),
               ("Garden Salad", "Mixed greens, house dressing", "VG GF"),
               ("Cobb Salad", "Chicken, bacon, egg, avocado", "GF")],
    "Mains": [("Cheeseburger", "Cheddar, lettuce, tomato, fries", ""),
              ("Grilled Salmon", "Rice, seasonal vegetables", "GF"),
              ("Mushroom Risotto", "Parmesan, truffle oil", "V GF"), ("Chicken Parmesan", "Spaghetti, marinara", ""),
              ("Steak Frites", "8 oz sirloin, peppercorn sauce", "GF"), ("Vegetable Curry", "Coconut, jasmine rice",
                                                                         "VG GF"),
              ("Fish and Chips", "Beer-battered cod, tartar sauce", ""), ("Pad Thai", "Rice noodles, peanuts, lime",
                                                                          ""),
              ("Margherita Pizza", "Tomato, mozzarella, basil", "V"), ("Beef Tacos", "Three tacos, salsa, lime", "GF"),
              ("Black Bean Burger", "Vegan bun, avocado", "VG")],
    "Desserts": [("Chocolate Cake", "With vanilla ice cream", "V"), ("Apple Pie", "Warm, cinnamon", "V"),
                 ("Cheesecake", "Berry sauce", "V"), ("Sorbet", "Two scoops, ask for flavours", "VG GF")],
    "Drinks": [("Coffee", "", "VG GF"), ("Tea", "", "VG GF"), ("Fresh Lemonade", "", "VG GF"),
               ("Soft Drinks", "Cola, lemon-lime, ginger ale", "VG GF"), ("Iced Tea", "", "VG GF"),
               ("Hot Chocolate", "", "V GF")],
}
SPECIALS = ("Lamb Shank with mashed potatoes", "Pan-Seared Scallops", "Butternut Squash Soup", "Fish Tacos",
            "Shepherd's Pie", "Lobster Roll", "Eggplant Parmesan", "Peach Cobbler", "Clam Chowder",
            "Short Rib Ragu")
LAYOUTS = ("one_column", "two_column", "pictures", "board", "specials")
MARK_WORDS = {"V": "vegetarian", "VG": "vegan", "GF": "gluten-free"}


def menu_details(n, rng):
    """The made-up facts of one menu: restaurant, address, phone, site, hours, layout, sections [(name, [(dish,
    description, marks, price)])] and specials [(dish, price)]."""
    name = rng.choice(RESTAURANTS)
    layout = LAYOUTS[n % len(LAYOUTS)]
    site = re.sub(r"[^a-z]", "", name.lower()) + ".example"
    d = {"name": name, "layout": layout, "site": site, "phone": f"(555) 555-01{rng.randint(0, 99):02d}",
         "address": f"{rng.randint(10, 990)} {rng.choice(STREETS)}, {rng.choice(TOWNS)}",
         "hours": rng.choice(("Open daily 11 am to 10 pm", "Mon-Sat 7 am - 3 pm", "Tue-Sun 5 pm to 11 pm")),
         "sections": [], "specials": []}
    if layout == "specials":
        for dish in rng.sample(SPECIALS, rng.randint(3, 5)):
            d["specials"].append((dish, f"${rng.randint(9, 34)}" + rng.choice(("", ".50", ".95"))))
        return d
    names = ["Drinks"] if layout == "board" else rng.sample(["Starters", "Salads", "Mains", "Desserts", "Drinks"],
                                                             rng.choice((3, 4)))
    order = [s for s in SECTIONS if s in names]
    for section in order:
        dishes = rng.sample(SECTIONS[section], min(len(SECTIONS[section]), rng.randint(3, 5)))
        low, high = {"Starters": (6, 14), "Salads": (9, 16), "Mains": (14, 34), "Desserts": (6, 11),
                     "Drinks": (2, 6)}[section]
        d["sections"].append((section, [(dish, about, marks, f"{rng.randint(low, high)}.{rng.choice(('00', '50', '95'))}")
                                        for dish, about, marks in dishes]))
    if layout == "pictures":
        mains = [x for sec, dishes in d["sections"] for x in dishes if sec != "Drinks"]
        d["pictured"] = [x[0] for x in rng.sample(mains, min(3, len(mains)))]
    return d


def draw_plate(draw, box, rng):
    """A simple drawing of a plate of food in box (a circle with coloured shapes on it)."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(235, 228, 214))
    draw.ellipse([x0 + 8, y0 + 8, x1 - 8, y1 - 8], fill=(255, 255, 255), outline=(180, 180, 180), width=3)
    for _ in range(5):
        cx, cy = rng.randint(x0 + 30, x1 - 30), rng.randint(y0 + 30, y1 - 30)
        size = rng.randint(10, 26)
        draw.ellipse([cx - size, cy - size, cx + size, cy + size],
                     fill=rng.choice([(190, 90, 40), (90, 150, 60), (230, 190, 80), (170, 40, 40), (120, 80, 50)]))


def draw_menu(d, rng):
    """One menu as a PIL image (see the module docstring)."""
    from PIL import Image, ImageDraw
    k = rng.randrange(8)
    board = d["layout"] in ("board", "specials")
    width = 1400 if d["layout"] == "two_column" else 1000
    lines = sum(1 + 0.85 * bool(x[1]) + 4.6 * (x[0] in d.get("pictured", [])) for _s, xs in d["sections"] for x in xs)
    height = 900 if board else max(1100, int(400 + 80 * len(d["sections"]) + 48 * lines / (2 if d["layout"] ==
                                                                                       "two_column" else 1)))
    bg = (32, 40, 36) if d["layout"] == "specials" else (20, 24, 30) if board else \
        rng.choice([(252, 248, 238), (255, 255, 255), (245, 240, 228)])
    ink = (240, 240, 235) if board else (25, 25, 25)
    accent = (240, 200, 90) if board else rng.choice([(140, 30, 30), (20, 70, 120), (40, 90, 50)])
    page = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(page)
    title, head, body, small = font(56, True, k), font(36, True, k), font(28, False, k), font(22, False, k)
    w = draw.textlength(d["name"], font=title)
    draw.text(((width - w) / 2, 40), d["name"], font=title, fill=accent)
    y = 130
    if d["layout"] == "specials":
        heading = "Today's Specials"
        w = draw.textlength(heading, font=head)
        draw.text(((width - w) / 2, y), heading, font=head, fill=ink)
        y += 90
        for dish, price in d["specials"]:
            draw.text((80, y), dish, font=body, fill=ink)
            pw = draw.textlength(price, font=body)
            draw.text((width - 80 - pw, y), price, font=body, fill=accent)
            y += 70
        return page
    columns = 2 if d["layout"] == "two_column" else 1
    col_w = (width - 120 - 60 * (columns - 1)) // columns
    col_x = [60 + i * (col_w + 60) for i in range(columns)]
    col, y0 = 0, y
    for section, dishes in d["sections"]:
        if columns == 2 and col == 0 and y > height * 0.52:
            col, y = 1, y0
        x = col_x[col]
        draw.text((x, y), section.upper(), font=head, fill=accent)
        y += 56
        for dish, about, marks, price in dishes:
            line = dish + (f"  ({marks})" if marks else "")
            price = f"${price}"
            draw.text((x, y), line, font=body, fill=ink)
            pw = draw.textlength(price, font=body)
            draw.text((x + col_w - pw, y), price, font=body, fill=ink)
            y += 38
            if about:
                draw.text((x + 10, y), about, font=small, fill=(150, 150, 150) if board else (90, 90, 90))
                y += 32
            if dish in d.get("pictured", []):
                draw_plate(draw, [x + col_w - 170, y, x + col_w, y + 130], rng)
                caption = f"Our {dish}"
                draw.text((x + col_w - draw.textlength(caption, font=small), y + 134), caption, font=small, fill=ink)
                y += 175
            y += 10
        y += 24
    footer = "V vegetarian   VG vegan   GF gluten-free"
    draw.text((60, height - 130), footer, font=small, fill=ink)
    draw.text((60, height - 90), f"{d['address']}  |  {d['phone']}  |  {d['site']}", font=small, fill=ink)
    draw.text((60, height - 55), d["hours"], font=small, fill=ink)
    return page


def menu_rows(d):
    """The rows of one made-up menu, from its own facts (see the module docstring)."""
    rows = []
    if d["layout"] == "specials":
        listed = "; ".join(f"{dish}, {price}" for dish, price in d["specials"])
        rows.append({"question": READ_Q, "answer": f"It is a specials board at {d['name']}. Today's Specials: "
                                                   f"{listed}."})
        rows.append({"question": "What are today's specials?", "answer": listed + "."})
        return [dict(r, credit=CREDIT, synthetic=True) for r in rows]
    parts = [f"{d['name']}."]
    for section, dishes in d["sections"]:
        said = []
        for dish, about, marks, price in dishes:
            words = dish + (f" ({', '.join(MARK_WORDS[m] for m in marks.split())})" if marks else "")
            said.append(f"{words}, ${price}" + (f": {about}" if about else "") +
                        (f" (below it, a small drawing of a plate of food captioned \"Our {dish}\")"
                         if dish in d.get("pictured", []) else ""))
        parts.append(f"{section}: " + "; ".join(said) + ".")
    parts.append("Key: V vegetarian, VG vegan, GF gluten-free.")
    parts.append(f"{d['address']}; phone {d['phone']}; {d['site']}; {d['hours']}.")
    rows.append({"question": READ_Q, "answer": " ".join(parts)})
    rows.append({"question": FROM_Q, "answer": f"{d['name']} (a made-up restaurant), {d['address']}; phone "
                                               f"{d['phone']}; web site {d['site']}; {d['hours']}."})
    every = [x for _section, dishes in d["sections"] for x in dishes]
    pick = every[len(every) // 2]
    rows.append({"question": f"How much is the {pick[0]}?", "answer": f"${pick[3]}."})
    veg = [x[0] for x in every if {"V", "VG"} & set(x[2].split())]
    rows.append({"question": "What vegetarian dishes are there?", "answer": (
        ("Marked vegetarian or vegan: " + ", ".join(veg) + ". ") if veg else "None is marked vegetarian or vegan. ")
        + ALLERGY_NOTE})
    gluten = [x[0] for x in every if "GF" in x[2].split()]
    rows.append({"question": "Which dishes are gluten-free?", "answer": (
        ("Marked GF (gluten-free): " + ", ".join(gluten) + ". ") if gluten else "None is marked gluten-free. ")
        + ALLERGY_NOTE})
    if d.get("pictured"):
        rows.append({"question": "What are the pictures on the menu?", "answer": "Small drawings of plates of food, "
                     "captioned " + ", ".join(f"\"Our {x}\"" for x in d["pictured"]) + "."})
    return [dict(r, credit=CREDIT, synthetic=True) for r in rows]


def make_menu(n, seed=SEED):
    """The n-th made-up menu as (file name, JPEG bytes, rows)."""
    rng = seeded(seed, n)
    d = menu_details(n, rng)
    page = draw_menu(d, rng)
    if rng.random() < 0.5:
        data = phone_photo(page, rng, strength=rng.uniform(0.3, 1.0))
    else:
        buffer = io.BytesIO()
        page.save(buffer, "JPEG", quality=90)
        data = buffer.getvalue()
    return f"menu-{d['layout']}-{n:05d}.jpg", data, menu_rows(d)


def build_synthetic_menus(limit):
    """The synthetic_menus pack (see the module docstring)."""
    from food_packs import with_twins
    return with_twins([make_menu(n) for n in range(limit)])


MENUS_PACKS = {
    "nypl_menus": (build_nypl_menus,
                   "The New York Public Library, \"What's on the Menu?\" (https://www.nypl.org/research/support/"
                   "whats-on-the-menu): menu data (dishes, prices, places and dates transcribed by volunteers) CC0 "
                   "from NYPL's published data dump; page pictures from images.nypl.org, each a menu published before "
                   "1931 (public domain in the United States) or marked \"No Known U.S. Copyright Restrictions\" or "
                   "CC0 by NYPL. From The New York Public Library."),
    "synthetic_menus": (build_synthetic_menus,
                        "Computer-made (synthetic) modern menus drawn with Pillow by packs/menus_packs.py from a fixed "
                        "seed: made-up restaurants, .example web sites and 555-01xx numbers, in one- and two-column "
                        "layouts, with drawn pictures of dishes, price boards and specials boards. CC0."),
}
MENUS_LIMITS = {"nypl_menus": 3000, "synthetic_menus": 2000}
MENUS_COMMONS_KEYS = ()


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check); --save writes the pictures."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a menus pack builder.")
    parser.add_argument("key", choices=sorted(MENUS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--save", default="")
    args = parser.parse_args(argv)
    entries = MENUS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
        if data and args.save:
            os.makedirs(args.save, exist_ok=True)
            with open(os.path.join(args.save, name), "wb") as f:
                f.write(data)
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
