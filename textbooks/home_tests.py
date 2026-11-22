"""At-home medical tests, with instructions for use, for the reference library (the owner's request of 2026-11-22).
Keys: home-tests (every book), hometest:<name>. The makers' own instructions (Instructions for Use and quick
reference guides) are in the manuals library's category "home_health_tests" (manuals/home_health_tests.py), as
links.

What this module builds, in plain words, each book starting with the safety notice ("Follow the test's own
instructions; faint lines can be hard to read; contact a doctor or pharmacist about any result."):
  - the FDA's "Home Use Tests" consumer pages (pregnancy, ovulation and menopause, COVID-19 and flu, HIV, blood
    glucose, cholesterol, drugs of abuse and alcohol, colon cancer (fecal occult blood and FIT), urinary tract
    infection, and the general advice on home tests), every page;
  - the FDA's list of authorised at-home over-the-counter COVID-19 (and flu) tests, with each test's maker, the
    sample it uses, and the links to its Instructions for Use and Quick Reference Instructions as FDA lists them;
  - CDC's guidance on testing at home for COVID-19 and flu (when to test, how to read a result, what to do next),
    kept whole with its text unchanged as CDC's terms ask;
  - a searchable book of home-use diagnostic tests from the FDA's open device databases (openFDA, public domain,
    CC0): for every over-the-counter test product code (pregnancy, ovulation, glucose meters and monitors,
    cholesterol and HbA1c, drugs of abuse, fecal occult blood, urinary nitrite, COVID-19 and respiratory virus
    tests, and the rest), a page with its classification and every 510(k), De Novo and PMA decision, and a page per
    brand with each model's device identifiers (UPC/GTIN barcodes) from the FDA's AccessGUDID database.

Not built: the CLIA-waived tests database (www.accessdata.fda.gov answers programs with its abuse-detection page),
and the text of the makers' Instructions for Use (written by the companies; FDA posting them does not make them
public domain): link-only, in NOT_INCLUDED and in the manuals category.

Licences: the FDA's and CDC's pages are works of the US government (FDA website policies: "They are in the public
domain and may be republished"; CDC's "Use of Agency Materials", with its conditions in the notice); openFDA's data
are public domain (CC0; each answer names open.fda.gov/license/, checked at every build).

Run from the repository's folder:
  python3 textbooks/home_tests.py hometest:device_records --out build/textbooks --limit 30
"""

import datetime
import json
import os
import re
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "health"
SAFETY = ("Follow the test's own instructions; faint lines can be hard to read; contact a doctor or pharmacist about "
          "any result.")
FDA_POLICY = "https://www.fda.gov/about-fda/about-website/website-policies"
FDA_TEXT = r"They are in the public domain and may be republished"
FDA_NOTICE = SAFETY + " A work of the US Food and Drug Administration (public domain: FDA website policies)."
API = "https://api.fda.gov"
LICENCE_URL = "https://open.fda.gov/license/"
TEST_SPECIALTIES = {"Clinical Chemistry", "Clinical Toxicology", "Hematology", "Microbiology", "Immunology",
                    "Pathology"}
NOT_TESTS = r"denture|container, specimen|cushion|pad\b"
# Home tests whose product code's name does not say "over the counter" (found from their device records,
# 2026-11-22): COVID-19 antigen self-tests under emergency use authorisation, the combined COVID-19, flu and RSV
# antigen home tests, and the OraQuick HIV self-test. Only their over-the-counter devices are listed.
EXTRA_CODES = ["QKP", "SCA", "MZF"]
CDC_NOTICE = SAFETY + (" Source: CDC (Centers for Disease Control and Prevention). Materials developed by CDC; "
                       "available free of charge on www.cdc.gov. Reference to specific commercial products, "
                       "manufacturers, companies, or trademarks does not constitute its endorsement or recommendation "
                       "by the U.S. Government, Department of Health and Human Services, or Centers for Disease "
                       "Control and Prevention. Kept whole with its text unchanged.")

GUIDES = [
    dict(K.guide(GROUP, "fda_home_use_tests", "Home use tests (FDA)", "At-home medical tests",
                 "US Food and Drug Administration (FDA)",
                 "https://www.fda.gov/medical-devices/in-vitro-diagnostics/home-use-tests",
                 r"^https://www\.fda\.gov/medical-devices/(in-vitro-diagnostics/home-use-tests|home-use-tests)"
                 r"(/[a-z0-9-]+)*$",
                 "Every page of the FDA's consumer guide to home use tests: what home tests are and how to use them "
                 "safely, and the pages on each kind of test (pregnancy, ovulation and menopause, COVID-19 and flu, "
                 "HIV, blood glucose, cholesterol, drugs of abuse and alcohol, fecal occult blood and FIT for colon "
                 "cancer screening, urinary tract infection, vaginal pH and others).", FDA_NOTICE, limit=60),
         licence_page=FDA_POLICY, licence_text=FDA_TEXT),
    dict(K.guide(GROUP, "fda_otc_covid_tests", "At-home over-the-counter COVID-19 and flu tests authorised by the FDA",
                 "At-home COVID-19 and flu tests", "US Food and Drug Administration (FDA)",
                 "https://www.fda.gov/medical-devices/coronavirus-covid-19-and-medical-devices/home-otc-covid-19-"
                 "diagnostic-tests",
                 r"^https://www\.fda\.gov/medical-devices/coronavirus-covid-19-and-medical-devices/(at-home-otc-"
                 r"covid-19-diagnostic-tests|at-home-covid-19-diagnostic-tests-frequently-asked-questions|"
                 r"home-otc-covid-19-diagnostic-tests)$",
                 "The FDA's list of at-home over-the-counter COVID-19 (and combined COVID-19 and flu) tests, with each "
                 "test's maker, type (antigen or molecular), sample, age range, and the links to its Instructions for "
                 "Use and Quick Reference Instructions, its expiration dates, and the FDA's questions and answers on "
                 "home tests.", FDA_NOTICE + " The Instructions for Use are the makers' documents, linked, not copied.",
                 limit=10),
         licence_page=FDA_POLICY, licence_text=FDA_TEXT),
    dict(K.guide(GROUP, "cdc_home_testing", "Testing at home for COVID-19 and flu (CDC)", "At-home COVID-19 and flu "
                 "tests", "Centers for Disease Control and Prevention (CDC)",
                 ["https://www.cdc.gov/covid/testing/index.html", "https://www.cdc.gov/flu/testing/index.html"],
                 r"^https://www\.cdc\.gov/(covid/testing|flu/testing|respiratory-viruses/testing)/[a-z0-9-]+\.html$",
                 "CDC's guidance on testing: when to test for COVID-19 and flu, the kinds of tests, how to use and "
                 "read a home test, what a positive or negative result means, repeat testing, and what to do next.",
                 CDC_NOTICE, limit=30),
         licence_page="https://www.cdc.gov/other/agencymaterials.html",
         licence_text=r"Most of the information on the CDC and ATSDR websites is not subject to copyright, is in the "
                      r"public domain", unchanged=True),
]


# ====================================================================== the device records (openFDA)

def api(path, params):
    """One openFDA answer ({} when nothing matches); the key OPENFDA_API_KEY is sent when the workflow has one."""
    import fda_recalls
    return fda_recalls.api_get(path, params)


def paged(path, search, limit=None):
    """Every record of an openFDA search (100 at a time), and the last answer's meta."""
    out, skip, meta = [], 0, {}
    while True:
        answer = api(path, {"search": search, "limit": 100, "skip": skip})
        meta = answer.get("meta") or meta
        rows = answer.get("results") or []
        out += rows
        skip += len(rows)
        total = (meta.get("results") or {}).get("total", 0)
        if not rows or skip >= total or skip >= 25000 or (limit and len(out) >= limit):
            return out, meta


def test_codes():
    """The over-the-counter and home-use diagnostic test product codes from the FDA's classification database:
    [{product_code, device_name, device_class, regulation_number, definition, medical_specialty_description}]."""
    rows, _meta = paged("device/classification", 'device_name:"over the counter" OR device_name:otc OR '
                        'device_name:"home use" OR device_name:"self-test" OR device_name:"over-the-counter"')
    keep = [r for r in rows if r.get("medical_specialty_description") in TEST_SPECIALTIES and
            not re.search(NOT_TESTS, r.get("device_name", ""), re.I)]
    have = {r["product_code"] for r in keep}
    for code in EXTRA_CODES:
        if code not in have:
            keep += paged("device/classification", f"product_code:{code}")[0][:1]
    return sorted(keep, key=lambda r: r.get("device_name", "").lower())


def decisions(code):
    """The 510(k) and De Novo decisions (openFDA device/510k) and PMAs (device/pma) of one product code, as rows."""
    out = []
    for r in paged("device/510k", f"product_code:{code}")[0]:
        kind = "De Novo" if str(r.get("k_number", "")).upper().startswith("DEN") else "510(k)"
        out.append((kind, r.get("k_number", ""), r.get("device_name", ""), r.get("applicant", ""),
                    r.get("decision_date", ""), r.get("decision_description", "")))
    for r in paged("device/pma", f"product_code:{code}")[0]:
        if r.get("supplement_number"):
            continue                                  # the original approvals only, not every supplement
        out.append(("PMA", r.get("pma_number", ""), r.get("trade_name", ""), r.get("applicant", ""),
                    r.get("decision_date", ""), r.get("decision_code", "")))
    return sorted(out, key=lambda x: x[4], reverse=True)


def device_records_book(name, work, cache=None, left_out=None, limit=None):
    """The searchable book of home-use test devices."""
    import build_textbooks as B
    import fda_recalls
    probe = api("device/classification", {"limit": 1})
    if not fda_recalls.licence_still_open(probe):
        left_out.append({"title": name, "reason": "openFDA's answer no longer names its public-domain licence page."})
        return None
    book = K.new_book("hometest_device_records", "Home-use medical tests: FDA device records by test type",
                      "At-home medical tests (device records)", GROUP, "US Food and Drug Administration (openFDA)",
                      K.CC0, LICENCE_URL, "https://www.fda.gov/medical-devices/in-vitro-diagnostics/home-use-tests",
                      "Every kind of over-the-counter and home-use diagnostic test the FDA classifies, from its open "
                      "databases: for each test type its classification and every 510(k), De Novo and PMA decision, "
                      "and a page per brand with each model's maker, description and device identifiers (UPC or GTIN "
                      "barcodes, from AccessGUDID).",
                      SAFETY + " Data from the US Food and Drug Administration through openFDA (public domain, CC0). "
                      "A product being in the FDA's databases does not mean the FDA recommends it.",
                      changes="the FDA's records made into web pages")
    book.pages.append(B.Page("safety", "Before you use a home test", "<p><strong>" + B.esc(SAFETY) + "</strong></p>"
                             "<p>Each test type's page lists the FDA's decisions about it; each brand's page lists "
                             "the models and the barcode numbers, so a product in your hand can be matched by its "
                             "UPC. The instructions for use are the maker's: see the manuals library (Home health "
                             "tests).</p>", 0, "About"))
    newest, paths = "", set()
    codes = test_codes()
    for c in codes:
        if limit and len(book.pages) > limit:
            break
        code, title = c["product_code"], c.get("device_name", "")
        nice = title[:1].upper() + title[1:].lower() if title.isupper() or title.istitle() else title
        rows = decisions(code)
        body = K.dl([("Product code", code), ("Device class", c.get("device_class")),
                     ("Regulation", f"21 CFR {c.get('regulation_number')}" if c.get("regulation_number") else ""),
                     ("Medical specialty", c.get("medical_specialty_description")),
                     ("Definition", c.get("definition"))])
        if rows:
            body += f"<h2>FDA decisions ({len(rows)})</h2>" + K.rows_table(
                rows, ("Kind", "Number", "Device name", "Applicant", "Decision date", "Decision"))
        book.pages.append(B.Page(B.slug(f"type-{code}", 30), f"{nice} (product code {code})", body, 0, nice))
        devices, meta = paged("device/udi", f"product_codes.code:{code} AND is_otc:true", limit and 200)
        newest = max(newest, meta.get("last_updated", ""))
        brands = {}
        for d in devices:
            brands.setdefault((d.get("brand_name") or "Unnamed").strip(), []).append(d)
        for brand, items in sorted(brands.items(), key=lambda kv: kv[0].lower()):
            table = []
            for d in items:
                gtins = ", ".join(i["id"] for i in d.get("identifiers") or [] if i.get("id"))
                table.append((d.get("version_or_model_number", ""), d.get("device_description", "")[:200],
                              d.get("company_name", ""), gtins, "yes" if d.get("is_otc") == "true" else "no",
                              d.get("commercial_distribution_status", "")))
            path = B.slug(f"{code}-{brand}", 70)
            while path in paths:
                path += "-2"
            paths.add(path)
            maker = items[0].get("company_name", "")
            book.pages.append(B.Page(path, f"{brand} ({maker}): {nice.lower()}", K.rows_table(
                table, ("Model", "Description", "Maker", "Device identifiers (UPC/GTIN)", "Over the counter",
                        "In commercial distribution")), 0, nice))
        book.originals.append({"url": f"{API}/device/udi.json?search=product_codes.code:{code}", "kind": "json"})
    book.published = newest
    book.version = f"openFDA device data updated {newest}" if newest else ""
    return book


def device_sign(name):
    """The device book's sign: openFDA's last update of the identifier and 510(k) data, by month."""
    parts = [api(p, {"limit": 1}).get("meta", {}).get("last_updated", "")[:7] for p in ("device/udi", "device/510k")]
    return K.sha(parts)


COLLECTION = K.Collection("hometest", GROUP, guides=GUIDES,
                          makers={"device_records": (device_records_book, device_sign)},
                          words={"home-tests": lambda: [f"hometest:{g['name']}" for g in GUIDES] +
                                 ["hometest:device_records"]})

GROUPS = {}
LICENCE_LINES = {
    "fda_home_tests": "www.fda.gov/about-fda/about-website/website-policies (checked at every build): FDA's web "
                      "pages \"are in the public domain and may be republished\". www.fda.gov's robots.txt allows "
                      "the pages (Crawl-delay 30, kept by the builder).",
    "openfda_devices": "api.fda.gov device data (classification, 510(k), PMA, UDI/AccessGUDID): each answer names "
                       "open.fda.gov/license/ (public domain, CC0), checked at every build; no robots.txt rules.",
}
NOT_INCLUDED = [
    ("CLIA-waived tests database (www.accessdata.fda.gov)", "Public domain, but www.accessdata.fda.gov answers "
     "programs with its abuse-detection page (robots.txt included, checked 2026-11-22). The same tests' FDA decisions "
     "are in hometest:device_records. Link-only. Index: "
     "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfClia/analyteswaived.cfm"),
    ("The makers' Instructions for Use and quick reference guides (including the copies FDA posts with EUA and "
     "clearance documents)", "Written by the companies; FDA's posting them does not make them public domain, and "
     "FDA's website policies say some posted material is copyrighted. They are linked, not copied: in the FDA list "
     "(hometest:fda_otc_covid_tests) and in the manuals library's category \"home_health_tests\". Index: "
     "https://www.fda.gov/medical-devices/coronavirus-covid-19-and-medical-devices/home-otc-covid-19-diagnostic-"
     "tests"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
