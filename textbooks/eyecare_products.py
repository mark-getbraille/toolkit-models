"""Eye care products for the reference library, in the group "Reference, home health care and first aid" (the
owner's request of 2026-11-22). Keys: eyecare-products (both books), eyeprod:<name>.

Two books, made by this module from official data (the medicine labels themselves are already the med:rx and med:otc
books of medications.py, by generic name: they are NOT rebuilt here; this module reuses medications.py's functions
to read a label and only quotes the parts listed below):
  eyeprod:eye_medicines      "Eye medicines by what they are for": artificial tears and lubricants, allergy drops,
                             redness relievers, antibiotic and antiviral drops and ointments, steroid drops, glaucoma
                             drops by class (prostaglandin analogues, beta blockers, alpha agonists, carbonic
                             anhydrase inhibitors, rho kinase inhibitors, miotics), dilating and numbing drops, and eye
                             washes. For each medicine one current DailyMed label whose product is given by the
                             ophthalmic route (the maker's or a brand's label before a repackager's, as medications.py
                             chooses): what it is for, its directions, warnings and storage IN THE LABEL'S OWN WORDS,
                             its ingredients, the address of the label on DailyMed, and the reference library's book
                             and page of its whole label (med:rx:<letters> or med:otc:<letters>). A redness reliever's
                             rebound-redness warning is there only when its label says it. The first page is the
                             National Eye Institute's "How to put in eye drops", whole (public domain).
  eyeprod:eye_care_devices   "Contact lenses, lens care products and other eye care devices": the FDA's device
                             classifications whose names say contact lens, lens care, lens case, spectacle, magnifier,
                             eye pad, eye patch, eye cup or eyelid, each with its definition, device class and
                             regulation, the FDA's 510(k) and PMA decisions, and the AccessGUDID records of each brand
                             (maker, model, description, UPC/GTIN barcodes, over the counter or not) from openFDA
                             (public domain, CC0). The FDA's contact lens pages (types, care, the never-tap-water rule,
                             hydrogen peroxide's neutralising step) are the eye care book eyes:fda_contact_lenses.

Makers' instructions-for-use leaflets (contact lenses, solutions, drop aids) are their copyright: link-only, through
the manual library's eye_care category; DailyMed's package pictures belong to the makers (the kit's personal-use
dailymed entries). Every page says: "Information, not medical advice: ask a pharmacist or eye doctor", and for
chemical splashes and eye injuries, the emergency note.

Run from the repository's folder:
  python3 textbooks/eyecare_products.py eyeprod:eye_medicines --out build/textbooks --limit 6
"""

import html
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "homehealth"
NOTICE = ("Information, not medical advice: ask a pharmacist or eye doctor. For a chemical splash or an eye injury, "
          "rinse the eye with clean running water for at least 15 minutes and call 911 (or your local emergency "
          "number). Poison Help: 1-800-222-1222 (US).")
HOW_TO = "https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/glaucoma/glaucoma-medicines/" \
         "how-put-eye-drops"

# (group title, what the group is for, [generic names searched on DailyMed]).
EYE_GROUPS = [
    ("Artificial tears and lubricants", "for dry, irritated eyes", ["carboxymethylcellulose", "polyvinyl alcohol",
                                                                   "hypromellose", "polyethylene glycol 400",
                                                                   "glycerin", "white petrolatum"]),
    ("Allergy eye drops", "for itchy eyes from allergies", ["ketotifen", "olopatadine", "alcaftadine", "cetirizine",
                                                            "naphazoline and pheniramine"]),
    ("Redness relievers", "to make red eyes look whiter", ["tetrahydrozoline", "naphazoline", "brimonidine"]),
    ("Antibiotic drops and ointments", "for bacterial eye infections (prescription)",
     ["erythromycin", "moxifloxacin", "ofloxacin", "ciprofloxacin", "tobramycin", "polymyxin b and trimethoprim",
      "gentamicin"]),
    ("Antiviral drops and gels", "for viral eye infections such as herpes (prescription)",
     ["trifluridine", "ganciclovir"]),
    ("Steroid eye drops", "for eye inflammation (prescription)", ["prednisolone acetate", "loteprednol",
                                                                 "dexamethasone", "fluorometholone", "difluprednate"]),
    ("Glaucoma drops: prostaglandin analogues", "lower eye pressure (prescription)",
     ["latanoprost", "travoprost", "bimatoprost", "tafluprost"]),
    ("Glaucoma drops: beta blockers", "lower eye pressure (prescription)", ["timolol", "betaxolol"]),
    ("Glaucoma drops: alpha agonists", "lower eye pressure (prescription)", ["brimonidine tartrate", "apraclonidine"]),
    ("Glaucoma drops: carbonic anhydrase inhibitors", "lower eye pressure (prescription)",
     ["dorzolamide", "brinzolamide"]),
    ("Glaucoma drops: rho kinase inhibitors", "lower eye pressure (prescription)", ["netarsudil"]),
    ("Glaucoma drops: miotics", "lower eye pressure, or treat age-related near-vision loss (prescription)",
     ["pilocarpine"]),
    ("Dilating drops", "widen the pupil for an eye exam (used by eye doctors)", ["tropicamide", "phenylephrine",
                                                                              "cyclopentolate", "atropine"]),
    ("Numbing drops", "numb the eye for an exam (used by eye doctors only)", ["proparacaine", "tetracaine"]),
    ("Eye washes", "rinse the eye", ["eye wash", "sterile eyewash"]),
]
OPHTHALMIC = re.compile(r"\bophthalmic\b", re.I)
MAX_LABELS = 4                    # labels of one search read in turn until one is given in the eye


def search_labels(name, cache=None):
    """[(setid, version, title)] of DailyMed labels for one generic name (its web service spls.json, the first 20),
    makers' labels before repackagers'."""
    import build_textbooks as B
    import medications as M
    url = f"{M.DM_SERVICES}/spls.json?" + urllib.parse.urlencode({"drug_name": name, "pagesize": 20})
    rows = json.loads(B.fetch(url, cache)).get("data", [])
    out = [(r["setid"], r.get("spl_version", 0), r.get("title", "")) for r in rows]
    return sorted(out, key=lambda r: bool(M.REPACKAGERS.search(r[2])))


def eye_label(name, cache=None):
    """The first label (medications.Label) for a generic name whose product is given by the ophthalmic route, or
    None."""
    import medications as M
    for setid, version, _title in search_labels(name, cache)[:MAX_LABELS * 3]:
        try:
            label = M.read_label(M.spl_xml(setid, version, cache))
        except Exception:  # noqa: BLE001 - a label that cannot be read: the next one
            continue
        if any(OPHTHALMIC.search(p.get("route", "")) for p in label.products):
            return label
    return None


def library_book(name, label):
    """("med:otc:t-z", "Tetrahydrozoline") the reference library's book and page of a label's medicine."""
    import medications as M
    kind = "otc" if label.doc_code == M.OTC_TYPE else "rx"
    pieces = M.OTC_PIECES if kind == "otc" else M.RX_PIECES
    generic = next((p["generic"] for p in label.products if p.get("generic")), name)
    page = M.display_name([w.strip() for w in re.split(r",| and ", generic.lower()) if w.strip()])
    piece = next(p for p in pieces if M.in_piece(page, p, pieces))
    return f"med:{kind}:{piece}", page


def label_parts_html(label):
    """The label's own uses, directions, warnings and storage (medications.sort_sections), as HTML; a part the
    label lacks says so."""
    import medications as M
    parts = M.sort_sections(M.read_label_copy(label))
    out = []
    for key, heading in (("uses", "What it is for"), ("dosing", "Directions"), ("warnings", "Warnings"),
                         ("storage", "Storage")):
        out.append(f"<h3>{heading} (the label's own words)</h3>")
        if parts[key]:
            out += [M.section_html(s, 4, M.SECTION_NAMES.get(s.code, "")) for s in parts[key]]
        else:
            out.append(f"<p>{M.NONE_SAID}</p>")
    return "\n".join(out)


def medicine_html(name, label):
    """One medicine's part of a group page: its label's source, ingredients, the parts and where its whole label is
    in the library."""
    import medications as M
    book, page = library_book(name, label)
    original = f"{M.DAILYMED}/drugInfo.cfm?setid={label.setid}"
    head = (f"<h2>{html.escape(page)}</h2><p>Label by {html.escape(label.company or 'its maker')}, version "
            f"{html.escape(str(label.version))}, dated {html.escape(label.date)}. Original: "
            f'<a href="{html.escape(original)}">{html.escape(original)}</a>. The whole label is in the reference '
            f"library's book {html.escape(book)}, page \"{html.escape(page)}\".</p>")
    return head + M.ingredients_html(label) + label_parts_html(label)


def how_to_page(cache=None):
    """The National Eye Institute's "How to put in eye drops" page, its main content whole (or None)."""
    import build_textbooks as B
    if not K.readable(HOW_TO, cache):
        return None
    text = B.fetch(HOW_TO, cache)
    m = re.search(r"<main\b[^>]*>(.*?)</main>", text, re.S)
    if not m:
        return None
    body = m.group(1)
    for pattern in K.DROP:
        body = re.sub(pattern, "", body, flags=re.S | re.I)
    body = re.sub(r"<img\b[^>]*>", "", body)
    return B.Page("how-to-put-in-eye-drops", "How to put in eye drops (National Eye Institute)",
                  body + f'<p>From the National Eye Institute (public domain): <a href="{HOW_TO}">{HOW_TO}</a></p>',
                  0, "Using eye drops")


def eye_medicines_book(name, work, cache=None, left_out=None, limit=None):
    """The book of eye medicines by what they are for (see the module docstring)."""
    import build_textbooks as B
    import medications as M
    left_out = left_out if left_out is not None else []
    if not M.licence_still_open():
        left_out.append({"title": name, "reason": "FDA's website policy no longer states that its labels' contents "
                                                  "are public domain."})
        return None
    book = K.new_book("eyeprod_eye_medicines", "Eye medicines by what they are for (DailyMed labels)",
                      "Eye care products", GROUP, "US National Library of Medicine (DailyMed) and the drug makers",
                      M.LICENCE, "https://www.fda.gov/about-fda/about-website/website-policies",
                      M.DAILYMED, "Eye drops and ointments grouped by what they are for, each with its official "
                      "label's own directions, warnings and storage, and where its whole label is in the library.",
                      NOTICE + " " + M.LABEL_NOTICE, changes="parts of the labels gathered by what the medicines "
                                                           "are for")
    page = how_to_page(cache)
    if page:
        book.pages.append(page)
        book.originals.append({"url": HOW_TO, "kind": "html"})
    else:
        left_out.append({"title": "How to put in eye drops (NEI)", "reason": "Its page could not be read."})
    groups = EYE_GROUPS[:limit] if limit else EYE_GROUPS
    newest = ""
    for title, purpose, names in groups:
        parts = [f"<p>{html.escape(title)}: {html.escape(purpose)}. {html.escape(NOTICE)}</p>"]
        for generic in names:
            label = eye_label(generic, cache)
            if label is None:
                left_out.append({"title": f"{title}: {generic}", "reason": "No DailyMed label for it given in the "
                                                                          "eye was found."})
                continue
            parts.append(medicine_html(generic, label))
            book.originals.append({"url": f"{M.DM_SERVICES}/spls/{label.setid}.xml", "kind": "xml"})
            newest = max(newest, label.date or "")
        if len(parts) > 1:
            book.pages.append(B.Page(B.slug(title, 60), title, "\n".join(parts), 0, "Eye medicines"))
    book.published = newest
    return book


def eye_medicines_sign(name):
    """The weekly sign: DailyMed's monthly release (the same sign as the medicine books)."""
    import medications as M
    return M.sign("med:otc:a-b")


# ====================================================================== contact lenses and other eye care devices

DEVICE_WORDS = ('device_name:"contact lens" OR device_name:"lens care" OR device_name:"lens case" OR '
                'device_name:spectacle OR device_name:magnifier OR device_name:"eye pad" OR device_name:"eye patch" '
                'OR device_name:"eye cup" OR device_name:eyelid')
NOT_HOME = re.compile(r"diagnostic|ophthalmodynamometer|gonioscop|surgical|implant|keratoprosthesis|laser|"
                      r"tonometer|electrode", re.I)


def eye_care_devices_book(name, work, cache=None, left_out=None, limit=None):
    """The book of contact lens and eye care device records (see the module docstring), made with home_tests.py's
    openFDA helpers."""
    import build_textbooks as B
    import fda_recalls
    import home_tests as H
    left_out = left_out if left_out is not None else []
    if not fda_recalls.licence_still_open(H.api("device/classification", {"limit": 1})):
        left_out.append({"title": name, "reason": "openFDA's answer no longer names its public-domain licence page."})
        return None
    book = K.new_book("eyeprod_eye_care_devices", "Contact lenses, lens care products and other eye care devices "
                      "(FDA device records)", "Eye care products", GROUP, "US Food and Drug Administration (openFDA)",
                      K.CC0, H.LICENCE_URL, "https://www.fda.gov/medical-devices/consumer-products/contact-lenses",
                      "The FDA's classifications of contact lenses, lens care products and cases, spectacle "
                      "magnifiers and other eye care devices, with the FDA's decisions and each brand's device "
                      "records (maker, model, barcodes).", NOTICE + " Data from the US Food and Drug Administration "
                      "through openFDA (public domain, CC0). A product being in the FDA's databases does not mean "
                      "the FDA recommends it. Contact lens solutions: never use tap water or saliva; with hydrogen "
                      "peroxide solutions, follow their neutralising step before the lens goes back in the eye, as "
                      "the FDA's contact lens pages say (eyes:fda_contact_lenses).",
                      changes="the FDA's records made into web pages")
    rows, _meta = H.paged("device/classification", DEVICE_WORDS)
    codes = sorted((r for r in rows if not NOT_HOME.search(r.get("device_name", ""))),
                   key=lambda r: r.get("device_name", "").lower())
    newest = ""
    for c in codes[:limit] if limit else codes:
        code, title = c["product_code"], c.get("device_name", "")
        body = K.dl([("Product code", code), ("Device class", c.get("device_class")),
                     ("Regulation", f"21 CFR {c.get('regulation_number')}" if c.get("regulation_number") else ""),
                     ("Definition", c.get("definition"))])
        decisions = H.decisions(code)
        if decisions:
            body += f"<h2>FDA decisions ({len(decisions)})</h2>" + K.rows_table(
                decisions[:200], ("Kind", "Number", "Device name", "Applicant", "Decision date", "Decision"))
        devices, meta = H.paged("device/udi", f"product_codes.code:{code}", 300)
        newest = max(newest, meta.get("last_updated", ""))
        table = []
        for d in devices[:300]:
            gtins = ", ".join(i["id"] for i in d.get("identifiers") or [] if i.get("id"))
            table.append((d.get("brand_name", ""), d.get("version_or_model_number", ""),
                          (d.get("device_description") or "")[:200], d.get("company_name", ""), gtins,
                          "yes" if d.get("is_otc") == "true" else "no"))
        if table:
            body += "<h2>Device records (AccessGUDID)</h2>" + K.rows_table(
                sorted(table), ("Brand", "Model", "Description", "Maker", "Device identifiers (UPC/GTIN)",
                                "Over the counter"))
        book.pages.append(B.Page(B.slug(f"{code}-{title}", 70), f"{title} (product code {code})", body, 0,
                                 "Eye care devices"))
        book.originals.append({"url": f"{H.API}/device/udi.json?search=product_codes.code:{code}", "kind": "json"})
    book.published = newest
    book.version = f"openFDA device data updated {newest}" if newest else ""
    return book


def devices_sign(name):
    """The device book's sign: openFDA's last update of its device data, by month."""
    import home_tests as H
    return H.device_sign(name)


COLLECTION = K.Collection("eyeprod", GROUP,
                          makers={"eye_medicines": (eye_medicines_book, eye_medicines_sign),
                                  "eye_care_devices": (eye_care_devices_book, devices_sign)},
                          words={"eyecare-products": lambda: ["eyeprod:eye_medicines", "eyeprod:eye_care_devices"]})

GROUPS = {}
LICENCE_LINES = {
    "eyeprod_labels": "DailyMed's labels: as medications.py (FDA's website policies, checked at every build: "
                      "labels' contents are public domain); only their own words are quoted. The NEI page on eye "
                      "drops is a US government work. openFDA device data: open.fda.gov/license/ (CC0), checked at "
                      "every build.",
}
NOT_INCLUDED = [
    ("Contact lens and solution makers' instructions for use (Bausch + Lomb, Alcon, Johnson & Johnson Vision, "
     "CooperVision)", "The makers' leaflets are their copyright; the FDA's 510(k) summaries list indications, not "
     "the leaflets' text. Link-only, in the manual library's eye_care category. Index: https://www.bausch.com/ , "
     "https://www.alcon.com/ , https://www.jnjvisioncare.com/ and https://coopervision.com/"),
    ("Blue-light and UV claims of glasses and lenses", "Only the FDA's own words are used: the device records' "
     "descriptions; no claim is added. Index: https://www.fda.gov/medical-devices/consumer-products"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
