"""Pack builders for MEDICINES, MEDICAL TOOLS AND SUPPLIES, and VETERINARY MEDICINES, with a focus on what people in
the United States and Canada meet at home, at the pharmacy, at the clinic and at the vet's:
  (A) supplies: bandages, adhesive strips, medical tape, splints and casts, syringes and needles, insulin pens and
      pumps, inhalers and nebulizers, pill organizers, first-aid kits, stethoscopes, otoscopes, pulse oximeters,
      blood-pressure cuffs, tourniquets, hospital beds, stretchers, AEDs, oxygen masks, surgical masks, face shields
      and medical gloves, knee scooters;
  (B) instruments: surgical instruments (scalpels, forceps, retractors, surgical scissors, needle holders) from
      Wikimedia Commons, and dental instruments photographed one by one (a CC BY 4.0 data set);
  (C) medicines: pills, tablets, capsules, blister packs, pill bottles, medicine bottles, vials and ampoules,
      vaccines, eye drops, nasal sprays, ointments, vitamins and dietary supplements, and named everyday medicines
      (acetaminophen/paracetamol, ibuprofen, aspirin, Tylenol, Advil, antacids);
  (D) veterinary: veterinary drugs, instruments and equipment, ivermectin, and vet clinics;
  (E) Open Images photos people checked for medical things (stethoscopes, syringes, pill organizers, first-aid kits,
      thermometers, medical gloves ...), and CDC Public Health Image Library photos of supplies (public domain);
  (F) public media: Voice of America's own public-domain photos on Commons (the only open public-media photos found).

Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name,
JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" where the source gives one
and "facts" (the Commons category). A picture with more than one question comes once with its JPEG and then again as
(None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

THE OWNER'S RULE FOR THIS COLLECTION: CURRENT ITEMS ONLY. Medical instruments, supplies and pills (human and
veterinary) must be things in use today, never historical: no Wellcome Collection, no Smithsonian or other museum
medical collections, no old catalogue drawings. A picture is left out when its words or its date suggest it is old:
a year before 2000 or a decade before the 2000s ("1950s"), a century ("19th century"), or the words "antique",
"historic(al)", "history of", "vintage", "museum", "accession", "catalogue number", "circa", "obsolete",
"old-fashioned", "replica", "exhibit", "World War", "Victorian" (OLD); when the Commons file is dated before 2000
(current_only); when a PHIL photo is undated or dated before 2000; and when an Open Images photographer is an
archive, museum, library or history body (OLD_SOURCE). Medicines the source says are discontinued or withdrawn are left out by the same words
("discontinued", "withdrawn", "no longer sold"). See test_med_vet.py.

Every answer is a fixed sentence written here from the source's own words, never by an AI model and never guessed:
  - the name of the Commons category a photo sits in ("Pill organizers" -> "This is a pill organizer: a box with a
    small lid for each day ..."), with one plain line on what it is for;
  - for medicines, careful words: "This looks like ibuprofen, a medicine for pain, fever and swelling." always
    followed by "Check the packaging or ask a pharmacist to be sure." (pill_packs.SAFETY). A model must never sound
    sure about a medicine;
  - "What is this instrument used for?" only from a fixed, safe, plain definition per category (INSTRUMENT and
    DENTAL_USES), never a medical instruction;
  - the file's own English caption, as "Describe this picture.", when it is a real, respectful one;
  - Open Images: only the labels people checked; PHIL: the CDC's own caption.
"What does the label say?" is NOT asked: none of these open sources gives a label's text exactly.

Safety (packs/SOURCE-RULES.md and the medical rules of medical_packs.py): no sexual content; no identifiable patients
(files whose words name a patient, or Open Images photos labelled Patient, Hospital gown, Injection, Surgery or
Medical procedure, are left out); nothing graphic (files whose words name an injury, a wound, blood, death, an
operation in progress or an operating room are left out; graphic medical pictures belong to medical_packs and
graphic_packs, which have their own rules); files whose words name a child are left out (medical photos of children
are only in childhood_illness). In the Commons supplies, instruments, medicines and veterinary packs, files whose words
name a person are left out too, so they show the things themselves and may be used for picture-making. The Open
Images and PHIL packs show people using the things (nurses, pharmacists, people checking their blood sugar): for
describing only (the kit's PEOPLE_AND_BODILY_PACK_KEYS), and so is voa_commons_photos (news photos of people).

The packs (all open; licences checked at the source, November 2026):
  med_commons_supplies     Commons categories of medical supplies and equipment (SUPPLY_SPECS). Each file's licence
                           checked on its own page: CC0, public domain, CC BY or an open government licence (OGL-ON,
                           OGL-Canada); never BY-SA, NC or ND (the kit's med_vet_commons_sa). Captions: Commons
                           structured data, CC0 ("All structured data from the file namespace is available under the
                           Creative Commons CC0 License", https://commons.wikimedia.org/wiki/Commons:Structured_data).
  med_commons_instruments  The same for surgical instruments (INSTRUMENT_SPECS), with "What is this instrument used
                           for?".
  med_commons_medicines    The same for medicines (MEDICINE_SPECS): pills, packs, bottles, vials, vitamins and named
                           everyday medicines, with "What is this medicine?" in careful words.
  vet_commons_medicine     The same for veterinary drugs, instruments, equipment and clinics (VET_SPECS).
  dental_instruments       Annotated Dental Instrument Dataset for YOLO Object Detection (Mendeley Data mh6zpc7y9g,
                           version 1, CC BY 4.0: "You can share, copy and modify this dataset so long as you give
                           appropriate credit, provide a link to the CC BY license, and indicate if changes were
                           made"): the original photos of 22 kinds of dental instruments, one instrument a photo,
                           from the authors' per-instrument folders (the "Group images" folder and the 512-pixel
                           stretched Roboflow copies are not used). "What is this instrument?" from the folder's name,
                           "What is this instrument used for?" from DENTAL_USES.
  open_images_medical      Open Images V7 (Google; labels CC BY 4.0, each photo's own licence checked: CC BY 2.0):
                           photos where people checked that a medical thing is there (OI_MEDICAL). Only photos Google
                           keeps on its own picture store (validation, test and the "boxable" training photos);
                           never fetched from Flickr. "What medical things are in this picture?" and "Is there ... ?"
                           (no only where people checked and rejected it).
  cdc_phil_supplies        CDC Public Health Image Library photos of medical supplies (syringes, vaccine vials, N95
                           respirators, gloves, glucose meters, test kits, naloxone ...), public domain (each item's
                           own copyright field must say "Permission is not required for public domain images", as
                           medical_packs.cdc_medical checks), dated 2000 or later, with the CDC's caption.
  voa_commons_photos       Voice of America's own photos copied to Commons (Category:Images from Voice of America,
                           1,084 files, November 2026: US elections and conventions, events, sport, VOA's studios):
                           "All text, audio and video material produced exclusively by the Voice of America is in the
                           public domain" (https://www.voanews.com/p/5338.html); each file's licence checked on its
                           Commons page, and files whose words name a wire or stock agency (AP, Reuters, AFP, Getty:
                           "not in the public domain", the same page) left out. The only public-media photos found
                           under an open licence (the public-media findings are in med_vet_sources.py). People kept:
                           for describing only. The current-items rule is not applied to it (it is not medical).

What already existed and is left alone: pill_packs (Taiwan FDA pills, Pharmassist blister packs, MEDISEG),
world_portal_packs.medpack_id, us_modern_sources.c3pi_pills (NLM C3PI, research); medical_packs (clinical pictures,
CDC PHIL illness photos, Wellcome and Europeana medical collections); home_packs.commons_appliances (Medical and
Digital thermometers, Glucose meters, Sphygmomanometers, Electronic arm blood pressure monitors) and
open_images_home (Glucose meter, Blood pressure monitor); everyday_packs.open_images_objects (Medicine, Pill, Capsule,
Pharmaceutical drug, Thermometer, Syringe: those labels are named in this pack's answers but a photo is chosen only
for a label open_images_objects does not ask about); bodily_packs.open_images_bodily (Bandage, Band-aid);
disability_packs (Wheelchairs, Electric wheelchairs, Rollators, Crutches, Walking sticks, Mobility scooters, Hearing
aids: not repeated here); events_safety_packs.commons_safety_photos (Personal protective equipment: here only the
narrower Surgical masks, Face shields and Medical gloves); us_modern_packs and canada_packs (pharmacies as places);
canada_sources.openfacts_ca and ca_recalls (products sold in Canada; Health Canada recall photos, which leave out
drug recalls). The non-open collections on these subjects (Commons BY-SA files, Open Food Facts supplements sold in
the US and Canada, DailyMed package labels of human and animal drugs) are in training-kit/kit/med_vet_sources.py.

    python packs/med_vet_packs.py med_commons_supplies --limit 8     (prints a few rows: a quick check)
"""

import collections
import csv
import json
import math
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, needs_description, pass_random
from build_packs import fetch_all, smaller, first_sentences
from food_packs import (with_twins, count_pictures, commons_get, credit_licence, sentence, listed, oi_lines,
                        oi_licence_name, OI_CLASSES, OI_PICTURE)
from home_packs import commons_fetch, file_name, NUDE
from expression_packs import CHILD, OI_CHILD, child_count
from mechanical_packs import NOT_A_CHILD, PLACES
from us_packs import NOT_SHOWN
from us_modern_packs import photo_year, commons_title
from land_industry_packs import INJURY
from device_packs import PERSON
from work_farm_mech_packs import (free_entries, spec_files, category_place, where_row, good_caption,
                                  PEOPLE_AT_WORK, CHILD_MORE, CAPTION_WORDS)
from pill_packs import SAFETY
from places import where

WHAT_Q = "What is this?"
MEDICINE_Q = "What is this medicine?"
INSTRUMENT_Q = "What is this instrument?"
USE_Q = "What is this instrument used for?"
PLACE_Q = "What kind of place is this?"
DESCRIBE_Q = "Describe this picture."
MEDICAL_Q = "What medical things are in this picture?"
QUESTIONS = {"thing": WHAT_Q, "medicine": MEDICINE_Q, "instrument": INSTRUMENT_Q, "place": PLACE_Q}
VET_SAFETY = "Check the packaging or ask a vet or pharmacist to be sure."
CURRENT_SINCE = 2000      # the owner's rule: current items only; files dated before this year are left out

# ----------------------------------------------------------------- the owner's rule: current items only

# Words that say a picture shows something old: a year before 2000, a decade before the 2000s, a century, or words
# of museums, antiques and history; and medicines the source says are discontinued or withdrawn.
DOSE = r"(?!\s?(mg|mcg|µg|ml|mL|g|iu|IU|units?|tablets?|capsules?|caplets?|count|ct|pieces|x)\b)"
OLD = re.compile(r"\b(1[0-8]\d\d|19\d\d)s?\b" + DOSE + r"|\b(19)?[1-9]0s\b|\b\d{1,2}(st|nd|rd|th)[- ]century\b|"
                 r"\b(antiques?|historic(al|ally)?|history of|vintage|museums?|accession\w*|catalogue (no|number)|"
                 r"circa|c\. ?1[5-9]\d\d|obsolete|old[- ]fashioned|replicas?|exhibit(s|ed|ion)?|world war|WWI+|"
                 r"civil war|victorian|edwardian|wellcome|smithsonian|army medical museum|discontinued|withdrawn|"
                 r"no longer (sold|made|available|marketed))\b|"
                 # museum accession numbers: "(AM 2017.92.14-13)", "1992.3.4", "inv. no. 123"
                 r"\b[A-Z]{1,4}\s?\d{2,4}\.\d{1,4}\.\d{1,4}|\b\d{4}\.\d{1,4}\.\d{1,4}\b|\binv(entory)?\.? ?no\b",
                 re.I)


def is_old(text):
    """True when a picture's words say it shows something old, historical or discontinued (OLD)."""
    return bool(OLD.search(text or ""))


def current_only(items, since=CURRENT_SINCE):
    """The items whose Commons file is dated `since` or later, or not dated (the file page's "date", read 50 files a
    request, as us_modern_packs.recent_only does for 1990); the others are noted as too old."""
    s, years = session(), {}
    titles = [commons_title(rows[0].get("credit")) for _, _, rows in items]
    wanted = [t for t in dict.fromkeys(titles) if t]
    for start in range(0, len(wanted), 50):
        try:
            data = commons_get(s, {"action": "query", "titles": "|".join(wanted[start:start + 50]),
                                   "prop": "imageinfo", "iiprop": "extmetadata",
                                   "iiextmetadatafilter": "DateTimeOriginal"})
        except RuntimeError:
            break                                 # Commons kept refusing: the words' check has been made already
        for p in ((data.get("query") or {}).get("pages") or {}).values():
            years[p.get("title")] = photo_year(((p.get("imageinfo") or [{}])[0]).get("extmetadata") or {})
        time.sleep(1)
    kept = []
    for item, title in zip(items, titles):
        if 0 < years.get(title, 0) < since:
            considered(item[0], item[1], f"dated {years[title]}: only current items ({since} onwards) are used")
            continue
        kept.append(item)
    return kept


# ----------------------------------------------------------------- safety words

# An operation in progress, an operating room, an open wound or a patient: left out (graphic or identifiable).
NOT_SHOWN_MEDICAL = re.compile(r"\b(patients?|wounds?|wounded|bleed\w*|blood\w*|gore|surgery in progress|during "
                               r"(an? |the )?(surgery|operation|procedure)|operating (room|theat(er|re)|table)|"
                               r"operation in progress|incisions?|surgeons? (operat\w*|perform\w*)|autops\w*|"
                               r"amputat\w*|cadavers?|necrop\w*|euthanas\w*|dissect\w*|"
                               r"drug (abuse|use|users?)|illicit|heroin|fentanyl|cocaine|meth(amphetamine)?|"
                               r"crack pipe|injecting drugs)\b", re.I)
# More words of medical and veterinary people (device_packs.PERSON and work_farm_mech_packs.PEOPLE_AT_WORK have the
# general ones).
MEDICAL_PEOPLE = re.compile(r"\b(nurses?|doctors?|physicians?|paramedics?|medics?|surgeons?|dentists?|"
                            r"pharmacists?|veterinarians?|vets? (tech\w*|nurse)|clinicians?|caregivers?|"
                            r"volunteers?|soldiers?|airm[ae]n|sailors?|marines?|corpsm[ae]n|residents?|"
                            r"hands|fingers|fingertips?|faces)\b", re.I)
# Medical words with "blood" in them that are not about blood shown: blood glucose, sugar and pressure.
NOT_BLOOD = re.compile(r"\bblood[- ](glucose|sugar|pressure)\b", re.I)


def left_out_because(title, text, people_ok=False, current=True):
    """Why a file is left out by its words, or "": nudity, a child, an injury, an operation or a patient, something
    old or discontinued (the owner's rule; only when current, as for every medical pack), and (unless people_ok) a
    person."""
    words = NOT_BLOOD.sub(" ", NOT_A_CHILD.sub(" ", f"{title} {text}"))
    if NUDE.search(words) or NOT_SHOWN.search(words):
        return "its words are about nudity or underwear, or it is an evidence photo"
    if CHILD.search(words) or CHILD_MORE.search(words) or re.search(r"\bp(a)?ediatric\w*", words, re.I):
        return "its words name a child (medical photos of children are left out here)"
    if INJURY.search(words) or NOT_SHOWN_MEDICAL.search(words):
        return "its words name an injury, blood, an operation, a patient or drug misuse"
    if current and is_old(words):
        return "its words say it is old, historical, a museum piece or discontinued (only current items are used)"
    if not people_ok and (PERSON.search(words) or PEOPLE_AT_WORK.search(words) or MEDICAL_PEOPLE.search(words)):
        return "its words name a person (this pack shows the things themselves)"
    return ""


# ----------------------------------------------------------------- specs

def spec(category, kind, answer, depth=0, use="", vet=False):
    """One Commons category: the kind of question ("thing", "medicine", "instrument", "place", or "caption" for a
    category whose photos are used only with their own caption), the fixed answer, how deep to look (0: the
    category's own files; 1: and its subcategories'), the plain line on what an instrument is used for, and whether
    it is a veterinary medicine (its safety line names the vet)."""
    return {"category": category, "kind": kind, "answer": answer, "depth": depth, "use": use, "vet": vet,
            "place": category_place(category)}


def thing(category, answer, depth=0):
    """A spec asking "What is this?"."""
    return spec(category, "thing", answer, depth)


def instrument(category, name, use, depth=0):
    """A spec asking "What is this instrument?" and "What is this instrument used for?"."""
    return spec(category, "instrument", f"This is {name}.", depth, use)


def medicine(category, answer, depth=0, vet=False):
    """A spec asking "What is this medicine?" in careful words: "This looks like ...", then the safety line."""
    return spec(category, "medicine", answer, depth, vet=vet)


def place(category, answer, depth=0):
    """A spec asking "What kind of place is this?"."""
    return spec(category, "place", answer, depth)


def caption_only(category, depth=0):
    """A spec whose photos are used only with their own caption (else set aside for a description)."""
    return spec(category, "caption", None, depth)


def file_rows(sp, found_in, title, credit, text):
    """The rows of one Commons file: the category's question and answer (a medicine's answer with the safety line),
    "What is this instrument used for?" for an instrument, the file's caption, and where it was taken when the
    category names a state or province; [] for a caption-only category without a usable caption."""
    where_ = sp["place"] if "," in sp["place"] else (category_place(found_in) or sp["place"])
    where_ = where_ or PLACES.get(title, "")
    facts = {"commons_category": found_in or sp["category"]}
    base = {"credit": credit, "facts": facts, **where(where_)}
    caption = good_caption(text, title)
    rows = []
    if sp["answer"]:
        answer = sp["answer"]
        if sp["kind"] == "medicine":
            answer = f"{answer} {VET_SAFETY if sp['vet'] else SAFETY}"
        rows.append(dict(base, question=QUESTIONS[sp["kind"]], answer=answer))
        if sp["use"]:
            rows.append(dict(base, question=USE_Q, answer=sp["use"]))
    if caption and (sp["answer"] or len(caption.split()) >= CAPTION_WORDS):
        rows.append(dict(base, question=DESCRIBE_Q, answer=caption))
    if rows:
        extra = where_row(rows[0], where_)
        if extra:
            rows.append(extra)
    return rows


# ----------------------------------------------------------------- the Commons engine

def commons_items(specs, limit, prefix, people_ok=False, current=True, also_out=None):
    """[(file name, picture address, rows)] from Commons specs, as work_farm_mech_packs.commons_items: the categories
    take turns in an order shuffled with pass_random, each an even share; only files under CC0, public domain, CC BY
    or an open government licence (free_entries); files left out by their words (left_out_because) are noted; a free
    file of a caption-only category without a usable caption is set aside for a description. current: the owner's
    rule (only current items) is applied; also_out(title, words) can give one more reason to leave a file out."""
    s, items, seen = session(), [], set()
    order = list(specs)
    pass_random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.3 / max(1, len(order))))
    want = int(limit * 1.3) + 2
    queues = [[sp, None] for sp in order]
    rounds = 0
    while len(items) < want and queues and rounds < 40:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            if listing_out_of_time():
                say(f"  {prefix}: stopped looking at half the time limit")
                queues = []
                break
            sp, files = q
            if files is None:
                files = [(t, c) for t, c in spec_files(s, sp) if t not in seen and not (current and is_old(c))]
                pass_random(sp["category"]).shuffle(files)
                say(f"Commons {sp['category']}: {len(files)} files")
            batch, q[1] = files[:share * 2], files[share * 2:]
            if not batch:
                queues.remove(q)
                continue
            found_in = dict(batch)
            got = 0
            try:
                entries = free_entries(s, [t for t, _ in batch])
            except RuntimeError as e:
                say(f"  Commons refused ({e}); {len(items)} pictures found")
                queues = []
                break
            for title, url, credit, text, raw in entries:
                if got >= share or title in seen:
                    continue
                words = f"{text} {raw} {found_in.get(title, '')}"
                why = left_out_because(title, words, people_ok, current) or (also_out(title, words) if also_out
                                                                             else "")
                if why:
                    considered(title, url, why)
                    continue
                rows = file_rows(sp, found_in.get(title, ""), title, credit, text)
                seen.add(title)
                if not rows:
                    needs_description(file_name(prefix, title), url, credit, credit_licence(credit), text=text,
                                      title=title, reason="its caption is missing or under six English words",
                                      place=category_place(found_in.get(title, "")) or sp["place"],
                                      page_url=credit.rsplit(", ", 1)[-1],
                                      extra={"commons_category": found_in.get(title) or sp["category"],
                                             "not_for_picture_making": people_ok})
                    continue
                items.append((file_name(prefix, title), url, rows))
                got += 1
            if not q[1]:
                queues.remove(q)
    pass_random(prefix + "-order").shuffle(items)
    return items[:want]


def commons_pack(specs, limit, prefix, people_ok=False):
    """commons_items, then the files dated before 2000 left out (the owner's rule), then the pictures downloaded."""
    items = current_only(commons_items(specs, limit, prefix, people_ok))
    fetched = commons_fetch(items)[:limit]
    say(f"{prefix}: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- med_commons_supplies

SUPPLY_SPECS = [
    thing("Bandages", "This is a bandage: a strip of cloth or gauze wrapped round a part of the body to cover or "
                      "support it.", 1),
    thing("Adhesive bandages", "This is an adhesive bandage (a sticking plaster, often called a Band-Aid): a small "
                               "pad on a sticky strip that covers a small cut.", 1),
    thing("Band-Aid", "This is a Band-Aid adhesive bandage: a small pad on a sticky strip that covers a small cut."),
    thing("Medical tape", "This is medical tape: tape that holds a dressing or a tube in place on the skin.", 1),
    thing("Surgical tape", "This is surgical tape: tape that holds a dressing in place on the skin."),
    thing("Triangular bandages", "This is a triangular bandage: a large triangle of cloth used as an arm sling or "
                                 "to hold a dressing in place."),
    thing("Splints", "This is a splint: a stiff support strapped along an injured limb to keep it still."),
    thing("Orthopedic casts", "This is a cast: a hard shell of plaster or fibreglass that holds a broken bone still "
                              "while it heals."),
    thing("Cervical collars", "This is a cervical collar (neck brace): it holds the neck still."),
    thing("Syringes", "This is a syringe: a tube with a plunger, used to give an injection or to measure liquid "
                      "medicine.", 1),
    thing("Hypodermic needles", "This is a hypodermic needle: the thin hollow needle on a syringe, used for "
                                "injections."),
    thing("Disposable syringes", "This is a disposable syringe: a plastic syringe used once and thrown away."),
    thing("Insulin syringes", "This is an insulin syringe: a small syringe with a fine needle, marked in units of "
                              "insulin."),
    thing("Autoinjectors", "This is an auto-injector: a pen-shaped device that injects one dose of medicine, such "
                           "as epinephrine for a severe allergy, when pressed against the thigh.", 1),
    thing("Infusion pumps", "This is an infusion pump: a machine that pushes fluid or medicine through an IV line "
                            "at a set rate.", 1),
    thing("Insulin pens", "This is an insulin pen: a pen-shaped injector that gives a measured dose of insulin."),
    thing("Insulin pumps", "This is an insulin pump: a small device worn on the body that gives insulin through a "
                           "thin tube."),
    thing("Inhalers", "This is an inhaler: a small device that sprays a measured dose of medicine to be breathed "
                      "in, often for asthma.", 1),
    thing("Nebulizers", "This is a nebulizer: a machine that turns liquid medicine into a mist breathed in through a "
                        "mask or mouthpiece.", 1),
    thing("Pill organizers", "This is a pill organizer: a box with a small lid for each day (or time of day), so "
                             "pills can be sorted ahead."),
    thing("First aid kits", "This is a first-aid kit: a box or bag of supplies, such as bandages and plasters, for "
                            "treating small injuries.", 1),
    thing("Stethoscopes", "This is a stethoscope: the listening tube with earpieces that doctors and nurses use to "
                          "hear the heart and lungs.", 1),
    thing("Ophthalmoscope", "This is an ophthalmoscope: a hand-held light for looking into the back of the eye."),
    thing("Reflex hammers", "This is a reflex hammer: a small rubber hammer for testing reflexes, such as the "
                            "knee jerk."),
    thing("Tongue depressor", "This is a tongue depressor: a flat wooden stick that holds the tongue down so the "
                              "throat can be seen."),
    thing("Wrist braces", "This is a wrist brace: a support strapped round the wrist to hold it still."),
    thing("Defibrillators", "This is a defibrillator: a machine that gives an electric shock to restart or steady "
                            "the heart.", 1),
    thing("Otoscopes", "This is an otoscope: a hand-held light with a cone, for looking into the ear."),
    thing("Pulse oximeters", "This is a pulse oximeter: a clip for a fingertip that shows the pulse and how much "
                             "oxygen is in the blood."),
    thing("Sphygmomanometers", "This is a blood-pressure cuff (sphygmomanometer): a cuff wrapped round the upper "
                               "arm and a gauge or screen that shows the blood pressure.", 1),
    thing("Tourniquets", "This is a tourniquet: a tight band for stopping heavy bleeding from a limb, or for "
                         "finding a vein before a blood test.", 1),
    thing("Hospital beds", "This is a hospital bed: a bed with rails and a frame that raises and lowers.", 1),
    thing("Stretchers", "This is a stretcher: a frame for carrying a person who is lying down.", 1),
    thing("Automated external defibrillators", "This is an AED (automated external defibrillator): a portable "
                                               "device that talks a helper through giving an electric shock to "
                                               "restart a heart.", 1),
    thing("Oxygen masks", "This is an oxygen mask: a mask over the nose and mouth that gives extra oxygen.", 1),
    thing("Intravenous therapy", "This is an IV (intravenous) drip: a bag of fluid on a pole that runs through a "
                                 "thin tube into a vein.", 1),
    thing("Surgical masks", "This is a surgical mask (medical face mask): a thin mask over the nose and mouth.", 1),
    thing("Face shields", "This is a face shield: a clear plastic visor that covers the whole face.", 1),
    thing("Medical gloves", "These are medical gloves: thin disposable gloves of nitrile, latex or vinyl.", 1),
    thing("Disposable gloves", "These are disposable gloves: thin gloves worn once and thrown away.", 1),
    thing("Hot-water bottles", "This is a hot-water bottle: a rubber bag filled with hot water to warm a bed or "
                               "ease aches.", 1),
    thing("Pregnancy test", "This is a home pregnancy test: a stick that shows lines or a word for the result.", 1),
    thing("Rapid diagnostic tests", "This is a rapid diagnostic test: a small test cassette that shows the result "
                                    "as lines in a few minutes."),
    thing("Cotton swabs", "These are cotton swabs: small sticks with cotton on the end."),
    thing("Ice packs", "This is an ice pack (cold pack), put on a sore or swollen place."),
    thing("Knee scooters", "This is a knee scooter: a wheeled frame to rest the knee on, used instead of crutches "
                           "when one foot cannot bear weight."),
    thing("COVID-19 rapid tests", "This is a COVID-19 rapid test: a small plastic test cassette that shows lines "
                                  "for the result."),
    caption_only("Medical supplies", 1),
    caption_only("Medical equipment in Canada", 1),
    caption_only("Medical equipment in the United States", 1),
]


def build_med_commons_supplies(limit):
    """The Commons medical supplies pack (files naming a person left out: may be used for picture-making)."""
    return commons_pack(SUPPLY_SPECS, limit, "medsup")


# ----------------------------------------------------------------- med_commons_instruments

INSTRUMENT_SPECS = [
    instrument("Scalpels", "a scalpel", "A scalpel is a very sharp small knife that surgeons use to cut skin and "
                                        "tissue.", 1),
    # (its own files only: its subcategories include Tweezers, used in fur, watch and craft workshops)
    instrument("Forceps", "a pair of forceps", "Forceps are tongs or tweezers for gripping and holding tissue or "
                                               "small objects."),
    instrument("Surgical forceps", "a pair of surgical forceps", "Surgical forceps grip and hold tissue, or clamp "
                                                                 "a blood vessel, during an operation.", 1),
    instrument("Surgical retractors", "a surgical retractor", "A retractor holds the edges of a cut apart, so the "
                                                              "surgeon can see and reach inside."),
    instrument("Surgical scissors", "a pair of surgical scissors", "Surgical scissors cut tissue, stitches or "
                                                                   "dressings."),
    instrument("Hemostatic forceps", "a pair of hemostatic forceps (a hemostat)", "A hemostat is a locking clamp "
                                                                           "that pinches a blood vessel shut or "
                                                                           "holds tissue."),
    instrument("Surgical needles", "a surgical needle", "A surgical needle is a curved needle used with thread to "
                                                        "stitch a cut closed."),
    instrument("Needle holders", "a needle holder", "A needle holder grips a curved needle firmly while stitches "
                                                    "are put in."),
    caption_only("Surgical instruments", 1),
]


def build_med_commons_instruments(limit):
    """The Commons surgical instruments pack (files naming a person, a patient or an operation left out)."""
    return commons_pack(INSTRUMENT_SPECS, limit, "medinst")


# ----------------------------------------------------------------- med_commons_medicines

def looks_like(name, what):
    """ "This looks like ibuprofen, a medicine for pain, fever and swelling." (the safety line is added later)."""
    return f"This looks like {name}, {what}."


MEDICINE_SPECS = [
    thing("Pills", "These are pills: small tablets or capsules of medicine to swallow.", 1),
    thing("Tablets (pharmacy)", "These are tablets: medicine pressed into small solid pills.", 1),
    thing("Capsules (pharmacy)", "These are capsules: medicine inside a small gelatin shell to swallow.", 1),
    thing("Blister packs", "This is a blister pack: a sheet of pills, each sealed in its own plastic bubble with foil "
                           "behind it, pushed out one at a time.", 1),
    thing("Pill bottles", "This is a pill bottle: a small plastic bottle of tablets or capsules, often orange with a "
                          "pharmacy label in the USA and Canada.", 1),
    thing("Prescription drugs", "This is a prescription medicine: one a pharmacist gives out only with a doctor's "
                                "or nurse practitioner's prescription."),
    thing("Medicine bottles", "This is a medicine bottle.", 1),
    thing("Vials", "This is a vial: a small glass bottle with a rubber stopper, holding a medicine or vaccine for "
                   "injection.", 1),
    thing("Ampoules", "This is an ampoule: a small sealed glass container of liquid medicine, snapped open at the "
                      "neck."),
    thing("Vaccines", "This is a vaccine: a medicine, usually injected, that teaches the body to fight an "
                      "infection.", 1),
    thing("COVID-19 vaccines", "This is a COVID-19 vaccine.", 1),
    thing("Eye drops", "These are eye drops: liquid medicine in a small squeeze bottle, put into the eye a drop at "
                       "a time.", 1),
    thing("Nasal sprays", "This is a nasal spray: medicine in a small bottle with a nozzle, sprayed into the "
                          "nose.", 1),
    thing("Ointments", "This is an ointment: a greasy medicine or skin cream, usually in a tube or tub.", 1),
    thing("Vitamins", "These are vitamins: tablets, capsules or gummies taken as a supplement.", 1),
    thing("Multivitamins", "These are multivitamins: a supplement with many vitamins and minerals in one tablet."),
    thing("Dietary supplements", "This is a dietary supplement: vitamins, minerals or other things taken as pills, "
                                 "capsules or powder in addition to food.", 1),
    medicine("Paracetamol", looks_like("acetaminophen (also called paracetamol)", "a medicine for pain and fever"),
             1),
    medicine("Tylenol", looks_like("Tylenol, a brand of acetaminophen", "a medicine for pain and fever"), 1),
    medicine("Ibuprofen", looks_like("ibuprofen", "a medicine for pain, fever and swelling"), 1),
    medicine("Advil", looks_like("Advil, a brand of ibuprofen", "a medicine for pain, fever and swelling")),
    medicine("Aspirin", looks_like("aspirin (acetylsalicylic acid)", "a medicine for pain and fever, also taken in "
                                                                       "a low dose to protect the heart"), 1),
    thing("Cough drops", "These are cough drops (throat lozenges): sweets with medicine that soothe a sore throat "
                         "or cough.", 1),
    thing("Hand sanitizers", "This is hand sanitizer: an alcohol gel or liquid that kills germs on the hands."),
    thing("Rubbing alcohol", "This is rubbing alcohol (isopropyl alcohol), used to clean skin and small wounds."),
    thing("Hydrogen peroxide", "This is hydrogen peroxide, a liquid used to clean small cuts and as a "
                               "disinfectant."),
    medicine("Naloxone", looks_like("naloxone (Narcan)", "an emergency medicine that reverses an opioid overdose"),
             1),
    medicine("Antacids", looks_like("an antacid", "a medicine that eases heartburn and indigestion"), 1),
    caption_only("Pharmaceutical drugs"),
    caption_only("Drugs in Canada", 1),
]


def build_med_commons_medicines(limit):
    """The Commons medicines pack (files naming a person, misuse or something old left out)."""
    return commons_pack(MEDICINE_SPECS, limit, "medicine")


# ----------------------------------------------------------------- vet_commons_medicine

VET_SPECS = [
    medicine("Veterinary drugs", "This looks like a veterinary medicine: a medicine made for animals, not people.",
             1, vet=True),
    medicine("Ivermectin", looks_like("ivermectin", "a medicine against worms and other parasites, used for animals "
                                                    "and for some illnesses in people"), 1, vet=True),
    thing("Veterinary equipment", "This is veterinary equipment: tools and machines used by vets to care for "
                                  "animals.", 1),
    thing("Veterinary instruments", "This is a veterinary instrument: a tool vets use to examine or treat "
                                    "animals.", 1),
    thing("Elizabethan collars", "This is an Elizabethan collar (a cone): a plastic cone round a pet's neck that "
                                 "stops it licking or scratching a wound or stitches while it heals.", 1),
    caption_only("Veterinary medicine in the United States", 1),
    caption_only("Veterinary medicine in Canada", 1),
    caption_only("Veterinary pharmacology", 1),
    thing("Ear tags", "This is an ear tag: a numbered tag clipped to an animal's ear, used on farm animals and on "
                      "wild animals that are being studied."),
    place("Veterinary clinics in the United States", "This is a veterinary clinic (vet's office) in the USA, where "
                                                     "pets are examined and treated.", 1),
    place("Veterinary clinics in Canada", "This is a veterinary clinic (vet's office) in Canada.", 1),
    place("Veterinary hospitals", "This is a veterinary hospital: an animal hospital.", 1),
]


def build_vet_commons_medicine(limit):
    """The Commons veterinary pack (animals kept; files naming a person, an injury or an operation left out)."""
    return commons_pack(VET_SPECS, limit, "vet")


# ----------------------------------------------------------------- dental_instruments (Mendeley Data, CC BY 4.0)

DENTAL_DATASET = "mh6zpc7y9g"
DENTAL_PAGE = "https://data.mendeley.com/datasets/mh6zpc7y9g/1"
DENTAL_CREDIT = ("Annotated Dental Instrument Dataset for YOLO Object Detection (R Girija, Alpa Gupta, Rakshak Anand, "
                 "Aravind Reddy Dhampetla, Tushank Kumar, Yash Kathait), Mendeley Data mh6zpc7y9g version 1, "
                 "doi:10.17632/mh6zpc7y9g.1, CC BY 4.0, " + DENTAL_PAGE)
EXTRACTION = "Extraction forceps are pliers-like forceps a dentist uses to grip a tooth and take it out"
# Each folder of the data set (the authors' name of the instrument) -> (what it is, what it is used for).
DENTAL_USES = {
    "Aji bone cutter": ("a bone cutter, a dental surgical instrument",
                        "A bone cutter trims or cuts small pieces of bone during dental surgery."),
    "Andrew Tongue Depressor": ("a tongue depressor (retractor), a dental instrument",
                                "A tongue depressor holds the tongue out of the way during dental work."),
    "Angled artery forceps": ("angled artery forceps, a surgical clamp",
                              "Artery forceps clamp a small blood vessel or hold tissue during surgery."),
    "Cross Bar elevator": ("a cross-bar dental elevator",
                           "A dental elevator loosens a tooth or a root before it is taken out."),
    "Curved gum scissors": ("curved gum scissors, a dental instrument",
                            "Gum scissors are small curved scissors for trimming gum tissue."),
    "Dental Aspirating Syringe": ("a dental aspirating syringe",
                                  "A dental syringe holds a cartridge of local anaesthetic, used to numb the mouth."),
    "Dental elevator": ("a dental elevator", "A dental elevator loosens a tooth or a root before it is taken out."),
    "Frazier Suction Tube": ("a Frazier suction tube",
                             "A suction tube is a thin metal tube that sucks away fluid during surgery."),
    "Mandibular Cowhorn forceps": ("cowhorn extraction forceps for the lower jaw",
                                   EXTRACTION + "; cowhorn forceps have two pointed beaks, for lower molars."),
    "Mandibular anterior extraction forceps": ("extraction forceps for the lower front teeth", EXTRACTION + "."),
    "Mandibular lower incisors forceps": ("extraction forceps for the lower incisors", EXTRACTION + "."),
    "Mandibular lower molar forceps": ("extraction forceps for the lower molars", EXTRACTION + "."),
    "Maxillary anterior canine forceps": ("extraction forceps for the upper front teeth and canines",
                                          EXTRACTION + "."),
    "Maxillary molar dental extraction forceps": ("extraction forceps for the upper molars", EXTRACTION + "."),
    "Maxillary upper incisors forceps": ("extraction forceps for the upper incisors", EXTRACTION + "."),
    "Maxillary upper molar forceps": ("extraction forceps for the upper molars", EXTRACTION + "."),
    "Maxillary upper molars extraction forceps": ("extraction forceps for the upper molars", EXTRACTION + "."),
    "Mayo Hegar needle holder": ("a Mayo-Hegar needle holder",
                                 "A needle holder grips a curved needle firmly while stitches are put in."),
    "Orthodontic ligature cutter": ("an orthodontic ligature cutter",
                                    "A ligature cutter snips the fine wires and ties used on braces."),
    "Straight artery forceps": ("straight artery forceps, a surgical clamp",
                                "Artery forceps clamp a small blood vessel or hold tissue during surgery."),
    "Straight tweezers": ("straight dental tweezers",
                          "Dental tweezers pick up and place small things such as cotton pellets."),
    "Wire Orthopedic Cutter": ("a wire cutter", "A wire cutter cuts surgical or orthodontic wire."),
}
DENTAL_FOLDERS = {k.lower(): k for k in DENTAL_USES}


def dental_class(member):
    """The data set's instrument name for one of its per-instrument zips ("Dental Elevator.zip" -> "Dental
    elevator"); "" for anything else ("Group images.zip": several instruments in one photo)."""
    base = member.rsplit("/", 1)[-1]
    return DENTAL_FOLDERS.get(base[:-4].strip().lower(), "") if base.lower().endswith(".zip") else ""


def dental_rows(cls):
    """The two rows of one photo of an instrument."""
    what, use = DENTAL_USES[cls]
    return [{"question": INSTRUMENT_Q, "answer": sentence(f"This is {what}"), "credit": DENTAL_CREDIT},
            {"question": USE_Q, "answer": use, "credit": DENTAL_CREDIT}]


def build_dental_instruments(limit):
    """The dental instruments pack: the 5 GB zip of original photos is read piece by piece (world_life_packs
    .remote_zip), each instrument's inner zip read as a stream (world_life_packs.zip_entries) only until its share
    of photos is taken, so only a part is downloaded."""
    from world_life_packs import remote_zip, zip_entries
    s = session()
    files = s.get(f"https://data.mendeley.com/public-api/datasets/{DENTAL_DATASET}/files?folder_id=root&version=1",
                  timeout=60).json()
    tools = next(f for f in files if f["filename"].lower().endswith("tools.zip"))
    outer = remote_zip(tools["content_details"]["download_url"], s)
    members = [m for m in outer.namelist() if dental_class(m)]
    pass_random("dental").shuffle(members)
    share = max(1, math.ceil(limit / max(1, len(members))))
    out = []
    for member in members:
        if build_packs.out_of_time() or len(out) >= limit:
            break
        cls, got = dental_class(member), 0
        try:
            with outer.open(member) as stream:
                for name, data in zip_entries(stream):
                    if got >= share:
                        break
                    if not re.search(r"\.(jpe?g|png)$", name, re.I) or name.startswith("__MACOSX"):
                        continue
                    picture = smaller(data)
                    pack_name = "dental-" + re.sub(r"[^\w.-]+", "_", f"{cls}-{name.rsplit('/', 1)[-1]}")
                    pack_name = pack_name.rsplit(".", 1)[0][:90] + ".jpg"
                    considered(pack_name, DENTAL_PAGE, "" if picture else "the picture could not be read")
                    if picture:
                        out.append((pack_name, picture, dental_rows(cls)))
                        got += 1
        except Exception as e:  # noqa: BLE001 - one instrument that cannot be read is left out
            say(f"  {cls}: left out ({type(e).__name__})")
        say(f"  {cls}: {got} photos")
    pass_random("dental-order").shuffle(out)
    return with_twins(out[:limit])


# ----------------------------------------------------------------- open_images_medical (Open Images V7)

# The labels a photo may be chosen for (none of them asked by another Open Images pack), with the plain words.
OI_MEDICAL = {
    "Stethoscope": "a stethoscope", "Medical thermometer": "a medical thermometer",
    "Infrared thermometer": "an infrared thermometer", "Pill organizer": "a pill organizer",
    "Nebulizer": "a nebulizer", "Scalpel": "a scalpel", "Surgical instrument": "surgical instruments",
    "Medical glove": "medical gloves", "Gauze": "gauze", "First aid kit": "a first-aid kit",
    "Neck brace": "a neck brace", "Stretcher": "a stretcher",
    "Automated external defibrillator": "an AED (automated external defibrillator)",
    "Oxygen mask": "an oxygen mask", "Blood glucose test strip": "blood-glucose test strips",
    "Dietary supplement": "dietary supplements", "Vitamin": "vitamins", "Prescription drug": "prescription medicine",
    "Medical bag": "a medical bag", "Adhesive bandage": "an adhesive bandage", "Dental instrument":
    "dental instruments", "Medical prescription": "a prescription", "Pet vitamins & supplements":
    "pet vitamins or supplements", "Medicine chest": "a medicine cabinet", "Medical equipment": "medical equipment",
}
# Labels that are named in the answer when people confirmed them, but never the reason a photo is chosen (other
# packs ask about them: open_images_objects, open_images_home, open_images_bodily).
OI_NAMED_TOO = {"Syringe": "a syringe", "Pill": "pills", "Capsule": "capsules", "Medicine": "medicine",
                "Pharmaceutical drug": "medicine", "Thermometer": "a thermometer", "Glucose meter":
                "a blood-glucose meter", "Blood pressure monitor": "a blood-pressure monitor", "Bandage": "a bandage",
                "Band-aid": "a sticking plaster"}
# Things a patient lies on or wears: with a person confirmed too, the photo is probably of a patient (left out).
OI_PATIENT_LIKE = {"Stretcher", "Neck brace", "Oxygen mask"}
OI_PEOPLE = {"Person", "Man", "Woman", "Human face", "Human body"}
# The plural words ("Are there ...?").
OI_PLURAL = {"surgical instruments", "medical gloves", "blood-glucose test strips", "dietary supplements", "vitamins",
             "dental instruments", "pet vitamins or supplements"}
# Photographers that are archives, museums, libraries or history bodies: their photos are old (the owner's rule).
OLD_SOURCE = re.compile(r"\b(histor\w*|heritage|archives?|museums?|librar(y|ies)|collections?|smithsonian|wellcome|"
                        r"national records)\b", re.I)
# A general label left out of the answer when a more specific one is there.
OI_COVERED = {"Medical equipment": set(OI_MEDICAL) - {"Medical equipment", "Dietary supplement", "Vitamin",
                                                      "Prescription drug", "Medical prescription",
                                                      "Pet vitamins & supplements"},
              "Thermometer": {"Medical thermometer", "Infrared thermometer"},
              "Medicine": {"Prescription drug", "Pharmaceutical drug", "Pill", "Capsule"},
              "Pharmaceutical drug": {"Prescription drug", "Pill", "Capsule"},
              "Surgical instrument": {"Scalpel"}, "Dietary supplement": {"Vitamin"}}
# Photos with one of these confirmed are left out: children, patients, operations, blood and injuries, nudity.
OI_LEAVE_OUT = set(OI_CHILD) | {"Patient", "Hospital gown", "Surgery", "Medical procedure", "Operating theater",
                                "Injection", "Blood", "Injury", "Nudity", "Swimwear", "Undergarment", "Halloween",
                                "Costume", "Zombie"}


def oi_medical_rows(labels, rng):
    """The rows of one Open Images photo from its {label: 1 (confirmed) or 0 (rejected)}: [] when no OI_MEDICAL
    label is confirmed. "What medical things are in this picture?" names the confirmed ones (at most six, the
    general ones left out when a specific one is there); "Is there ... ?" is asked once, yes for a confirmed label
    or no for one people checked and rejected."""
    yes = {n for n, c in labels.items() if c == 1}
    no = {n for n, c in labels.items() if c == 0}
    if not yes & set(OI_MEDICAL) or (yes & OI_PATIENT_LIKE and yes & OI_PEOPLE):
        return []
    words = {**OI_NAMED_TOO, **OI_MEDICAL}
    named = []
    for n in list(OI_MEDICAL) + list(OI_NAMED_TOO):
        if n in yes and not (OI_COVERED.get(n, set()) & yes) and words[n] not in named:
            named.append(words[n])
    rows = [{"question": MEDICAL_Q, "answer": f"I can see {listed(named[:6])}."}]
    def ask(n, yes_answer):
        """ "Is there a stethoscope ...?" or "Are there medical gloves ...?" and its answer."""
        word = OI_MEDICAL[n]
        plural = word in OI_PLURAL
        question = f"{'Are' if plural else 'Is'} there {word} in this picture?"
        if yes_answer:
            return {"question": question, "answer": f"Yes, there {'are' if plural else 'is'} {word} in this picture."}
        return {"question": question, "answer": f"No, I can't see {'any ' if plural else ''}{word} in this picture."}

    absent = sorted(n for n in no & set(OI_MEDICAL) if n != "Medical equipment")
    present = sorted(n for n in yes & set(OI_MEDICAL) if n != "Medical equipment")
    if absent and rng.random() < 0.5:
        rows.append(ask(rng.choice(absent), False))
    elif present:
        rows.append(ask(rng.choice(present), True))
    return rows


def build_open_images_medical(limit):
    """The Open Images medical things pack: the labels people checked on the train, validation and test sets
    (bodily_packs.oi_label_lines), photos with a leave-out label confirmed or a Flickr title naming a child left
    out, only photos whose own licence is CC BY (or CC0) and that need no turning, and only photos on Google's own
    picture store (never from Flickr); the rarest labels first."""
    from bodily_packs import oi_label_lines, OI_BOXABLE, OI_ALL_IMAGES
    s, rng = session(), pass_random("oi-medical")
    names = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            names.setdefault(line[1], line[0])
    wanted = set(OI_MEDICAL) | set(OI_NAMED_TOO) | OI_PEOPLE
    mids = {names[n]: n for n in wanted if n in names}
    leave_mids = {names[n] for n in OI_LEAVE_OUT if n in names}
    labels, leave = oi_label_lines(s, mids, leave_mids)
    labels = {k: v for k, v in labels.items() if k not in leave and any(c == 1 and n in OI_MEDICAL
                                                                         for n, c in v.items())}
    say(f"Open Images: {len(labels)} photos with a medical label confirmed")
    boxable = {r["ImageID"] for r in csv.DictReader(oi_lines(s, OI_BOXABLE)) if r["ImageID"] in labels}
    photos = {}
    for url in OI_ALL_IMAGES:
        subset = "train" if "train" in url else "validation" if "validation" in url else "test"
        for r in csv.DictReader(oi_lines(s, url)):
            image_id = r["ImageID"]
            if image_id not in labels or (subset == "train" and image_id not in boxable):
                continue
            if CHILD.search(r.get("Title") or "") or is_old(r.get("Title") or "") or \
                    OLD_SOURCE.search(r.get("Author") or ""):
                continue
            licence = oi_licence_name(r.get("License") or "", image_id)
            if licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
                photos[image_id] = (OI_PICTURE.format(subset=subset, image_id=image_id), licence,
                                    clean(r.get("Author")) or "an unnamed photographer",
                                    r.get("OriginalLandingURL") or "")
    counts = collections.Counter(n for v in labels.values() for n, c in v.items() if c == 1)
    items = []
    for image_id in sorted(photos):
        rows = oi_medical_rows(labels[image_id], rng)
        if not rows:
            continue
        address, licence, author, page = photos[image_id]
        credit = f"Photo by {author}{f' ({page})' if page else ''}, {licence}; labels from Open Images V7 (Google), " \
                 "CC BY 4.0"
        rarest = min(counts[n] for n, c in labels[image_id].items() if c == 1 and n in OI_MEDICAL)
        items.append((rarest + rng.random(), f"oi-medical-{image_id}.jpg", address,
                      [dict(r, credit=credit) for r in rows]))
    items.sort(key=lambda x: x[0])
    chosen = [x[1:] for x in items[:int(limit * 1.1) + 2]]
    pass_random("oi-medical-order").shuffle(chosen)
    say(f"Open Images: {len(items)} free medical photos; {len(chosen)} chosen")
    return with_twins(fetch_all(chosen, workers=8)[:limit])


# ----------------------------------------------------------------- cdc_phil_supplies (CDC PHIL, public domain)

PHIL_SUPPLY_KEYWORDS = ("syringe", "vaccine vial", "vial", "N95", "respirator", "face shield", "surgical mask",
                        "gloves", "gown", "personal protective equipment", "hand sanitizer", "thermometer",
                        "glucose meter", "insulin", "inhaler", "stethoscope", "first aid kit", "test kit",
                        "rapid test", "swab", "pills", "tablets", "medication", "naloxone", "sharps container",
                        "intravenous", "nebulizer", "blood pressure cuff", "pulse oximeter", "auto-injector")
# A PHIL caption must name one of these things (the photo is about a supply, not a scene).
SUPPLY_WORDS = re.compile(r"\b(syringes?|needles?|vials?|vaccines?|N95|respirators?|face ?shields?|masks?|gloves?|"
                          r"gowns?|goggles|personal protective equipment|PPE|hand sanitizers?|thermometers?|"
                          r"glucose meters?|glucometers?|test strips?|insulin|inhalers?|stethoscopes?|first[- ]aid|"
                          r"test kits?|rapid tests?|swabs?|pills?|tablets?|capsules?|medications?|medicines?|"
                          r"naloxone|sharps containers?|IV bags?|intravenous|nebulizers?|blood pressure cuffs?|"
                          r"pulse oximeters?|auto-?injectors?|bandages?|gauze)\b", re.I)
# Not a photo of a supply in use today: microscope pictures, drawings, laboratory animals, and sexual-health photos
# (not wanted here).
PHIL_NOT_SUPPLY = re.compile(r"\b(micrograph\w*|microscop\w*|magnifi\w*|electron|culture\w*|colon(y|ies)|agar|petri|"
                             r"illustration|drawing|diagram|cartoon|infographic|poster|graphic|chart|map|"
                             r"mouse|mice|rats?|monkeys?|macaques?|guinea pigs?|rabbits?|ferrets?|condoms?|"
                             r"sexual\w*)\b", re.I)


def phil_caption(text):
    """A PHIL caption as a description: its first two sentences without the lead-in ("This image depicts"), as a
    sentence; "" when under six words."""
    from medical_packs import strip_lead
    text = first_sentences(clean(text), 60)
    text = strip_lead(text)
    return sentence(text) if len(text.split()) >= CAPTION_WORDS else ""


def phil_left_out(r):
    """Why a PHIL record is left out ("" when kept): not public domain, undated or dated before 2000 (the owner's
    rule), no supply named, not a photo of a supply, a child, an injury, an operation or a patient, or old words."""
    caption = r.get("caption") or ""
    year = int(m.group(0)) if (m := re.search(r"\b(19|20)\d\d\b", r.get("year") or "")) else 0
    if not r.get("public"):
        return "not marked public domain"
    if year < CURRENT_SINCE:
        return f"dated {year or 'nothing'}: only current items ({CURRENT_SINCE} onwards) are used"
    if not SUPPLY_WORDS.search(caption):
        return "its caption names no medical supply"
    if PHIL_NOT_SUPPLY.search(caption):
        return "not a photo of a supply (a microscope picture, a drawing, a laboratory animal or sexual health)"
    why = left_out_because("", caption, people_ok=True)
    return why


def build_cdc_phil_supplies(limit):
    """The CDC PHIL supplies pack: keyword searches (medical_packs.phil_records: public-domain items with a picture
    and a caption), each record checked by phil_left_out, the CDC's caption as "Describe this picture."."""
    from medical_packs import phil_records, phil_credit
    items = []
    for r in phil_records(PHIL_SUPPLY_KEYWORDS):
        if len(items) >= limit * 1.2 + 2 or listing_out_of_time():
            break
        name = f"phil-{r['pid']}.jpg"
        why = phil_left_out(r)
        caption = "" if why else phil_caption(r["caption"])
        if why or not caption:
            considered(name, r.get("picture"), why or "its caption is too short")
            continue
        items.append((name, r["picture"], [{"question": DESCRIBE_Q, "answer": caption, "credit": phil_credit(r),
                                            "facts": {"phil_id": r["pid"]}}]))
    say(f"CDC PHIL supplies: {len(items)} usable")
    return with_twins(fetch_all(items, workers=3)[:limit])


# ----------------------------------------------------------------- voa_commons_photos (Voice of America, public domain)

VOA_CATEGORY = "Images from Voice of America"
VOA_WHO = "It is a photo by Voice of America (VOA), the US government's international broadcaster."
# Wire and stock agencies whose photos VOA uses under licence ("not in the public domain", VOA's copyright
# statement): a file whose words name one is left out, whatever tag it carries on Commons.
WIRE = re.compile(r"\b(AP|Associated Press|Reuters|AFP|Agence France[- ]Presse|Getty|EPA|Shutterstock|"
                  r"Alamy|via AP|AP Photo)\b")


def voa_caption(text):
    """A VOA caption without the marks of a social-media post: "@VOANews" goes, "#DemConvention" becomes
    "DemConvention", " -- " becomes a comma; the caption as a sentence."""
    text = re.sub(r"\s*@\w+\.?", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    text = re.sub(r"\s+--+\s+", ", ", text)
    return sentence(clean(text).strip(" ,"))


def voa_not_own(title, words):
    """Why a file of the VOA category is left out besides the shared word checks: a wire or stock agency named."""
    return "its words name a wire or stock agency (not VOA's own photo)" if WIRE.search(f"{title} {words}") else ""


def build_voa_commons_photos(limit):
    """VOA's own photos copied to Commons (their licence checked file by file: public domain as US government work,
    {{PD-USGov-VOA}}), with their caption, and "Who took this photo?". People are kept (news, politics, events,
    sport): for describing only. Files naming an injury, a death, a child or nudity, or a wire agency, are left
    out; the owner's current-items rule is for the medical packs and is not applied here."""
    items = commons_items([caption_only(VOA_CATEGORY)], limit, "voa", people_ok=True, current=False,
                          also_out=voa_not_own)
    items = [(n, u, [dict(r, answer=voa_caption(r["answer"])) if r["question"] == DESCRIBE_Q else r for r in rows]
              + [{"question": "Who took this photo?", "answer": VOA_WHO, "credit": rows[0]["credit"]}])
             for n, u, rows in items]
    fetched = commons_fetch(items)[:limit]
    say(f"voa_commons_photos: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what}: captions CC0; pictures CC0, public domain, CC BY or an open government "
                  "licence (OGL-ON, OGL-Canada), each with its author and file page below. "
                  "https://commons.wikimedia.org. Changes: pictures made smaller; answers written from the category "
                  "names. Current items only (nothing dated or described as before 2000).")
MED_VET_PACKS = {
    "med_commons_supplies": (build_med_commons_supplies, COMMONS_CREDIT.format(
        what="categories of medical supplies and equipment (bandages, syringes, inhalers, first-aid kits, "
             "stethoscopes, hospital beds, masks and gloves)")),
    "med_commons_instruments": (build_med_commons_instruments, COMMONS_CREDIT.format(
        what="categories of surgical instruments (scalpels, forceps, retractors, scissors, needle holders)")),
    "med_commons_medicines": (build_med_commons_medicines, COMMONS_CREDIT.format(
        what="categories of medicines (pills, blister packs, pill bottles, vials, vaccines, vitamins and everyday "
             "medicines)")),
    "vet_commons_medicine": (build_vet_commons_medicine, COMMONS_CREDIT.format(
        what="categories of veterinary drugs, instruments, equipment and clinics")),
    "dental_instruments": (build_dental_instruments,
                           DENTAL_CREDIT + ". Original photos of 22 kinds of dental instruments, one a photo. "
                           "Changes: pictures made smaller; answers written from the instrument names."),
    "open_images_medical": (build_open_images_medical,
                            "Open Images V7 (Google): image-level labels verified by people, CC BY 4.0; photos CC BY "
                            "2.0, each photographer credited below (only photos on Google's own store). "
                            "https://storage.googleapis.com/openimages/web/index.html"),
    "cdc_phil_supplies": (build_cdc_phil_supplies,
                          "CDC Public Health Image Library (PHIL), https://phil.cdc.gov: public-domain photographs "
                          "only (each item's own copyright field checked), dated 2000 or later, captions by the CDC. "
                          "Changes: pictures made smaller; captions shortened."),
    "voa_commons_photos": (build_voa_commons_photos,
                           "Voice of America photos copied to Wikimedia Commons (Category:Images from Voice of "
                           "America): 'All text, audio and video material produced exclusively by the Voice of "
                           "America is in the public domain' (https://www.voanews.com/p/5338.html); each file's "
                           "licence checked on its Commons page; captions CC0 (Commons structured data) or from the "
                           "file page. Changes: pictures made smaller."),
}

# How many pictures a full build takes from each (about what each offers after the checks).
MED_VET_LIMITS = {
    "med_commons_supplies": 2000,     # about 35 categories; most of the larger ones (bandages, syringes, stretchers)
    #                                   lose many files to the person and licence checks
    "med_commons_instruments": 600,   # about 1,000 surgical-instrument files under CC BY or freer
    "med_commons_medicines": 1500,    # about 25 categories, the pill and vitamin ones the largest
    "vet_commons_medicine": 500,      # about 800 files; many vet photos show people and are left out
    "dental_instruments": 800,        # 22 instruments, about 38 original photos each
    "open_images_medical": 900,       # 984 photos pass the licence and picture-store checks (of 2,184 with a
    #                                   medical label confirmed)
    "cdc_phil_supplies": 400,         # PHIL photos of supplies dated 2000 or later
    "voa_commons_photos": 700,        # 1,084 files; those with a caption of six words or more
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one medicine, medical supply or veterinary pack builder.")
    parser.add_argument("key", choices=sorted(MED_VET_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = MED_VET_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    questions = collections.Counter(row["question"] for _, _, row in entries)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child, "
        f"{len(build_packs.NEEDS)} set aside for a description; questions: " +
        ", ".join(f"{q} {n}" for q, n in questions.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
