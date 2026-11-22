"""FDA food, drug and device recalls and drug shortages for the reference library (the owner's request of 2026-11-22).
Keys: recalls (the last 24 months and the shortages), recalls-all (every month since June 2012), fda:recalls (the
same as recalls-all), fda:recalls:<YYYY-MM> (one month), fda:shortages.

What this module builds, in plain words:
  - one book per month of the FDA Enforcement Report: every recall of food (and cosmetics), human and animal drugs,
    and medical devices that FDA classified that month, one page per recall event (the firm, the reason, the class
    and what it means, the products with their lot codes, where they were sold, the status), in three parts (food,
    drugs, devices); the current month's book also lists the latest company recall announcements FDA posted (titles,
    dates and links only: their text is written by the companies);
  - one book of the current drug shortages (FDA's drug shortage list): one page per medicine with each package's
    availability, the reason, the company's contact and the therapeutic category.

Where it comes from: openFDA's API (api.fda.gov), the FDA's official programmers' interface, which answers programs
(it has no robots.txt; openFDA's download site download.open.fda.gov and open.fda.gov refuse programs with "Access
Denied", so their bulk files are not used). Without a key the API allows 1,000 requests a day from one address
(240 a minute); a month's book needs about four, and every request waits for the pause. If the owner puts a free
openFDA key in the workflow as OPENFDA_API_KEY (none exists in this repository's secrets now), it is sent too.

Licence: every API answer names its licence page, https://open.fda.gov/license/ ("unless otherwise noted, the
content, data, documentation, code, and related materials on openFDA is public domain and made available with a
Creative Commons CC0 1.0 Universal dedication"); each build checks that the answer still names it (as medications.py
does for the drug labels). The API's own disclaimer is shown on every book: do not rely on it for medical decisions.

The daily refresh (the workflow's daily schedule, sources.expand_keys "pub:daily") rebuilds this month's recalls and
the shortages; a past month is a kept version, rebuilt by the weekly check when its recalls change (a recall closed,
or one reclassified).

Run from the repository's folder:
  python3 textbooks/fda_recalls.py fda:recalls:2026-10 --out build/textbooks
  python3 textbooks/fda_recalls.py fda:shortages --out build/textbooks --limit 20
"""

import datetime
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "health"
API = "https://api.fda.gov"
LICENCE_URL = "https://open.fda.gov/license/"
FIRST_MONTH = "2012-06"
PUBLISHER = "US Food and Drug Administration (openFDA)"
DISCLAIMER = ("openFDA's own words: \"Do not rely on openFDA to make decisions regarding medical care. While we make "
              "every effort to ensure that data is accurate, you should assume all results are unvalidated.\" "
              "Check fda.gov/recalls or ask a pharmacist or doctor.")
NOTICE = ("Data from the US Food and Drug Administration through openFDA (api.fda.gov): public domain, CC0 1.0 "
          "(open.fda.gov/license). " + DISCLAIMER)
RSS = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/recalls/rss.xml"
KINDS = [("food", "Food and cosmetics"), ("drug", "Drugs (human and animal)"), ("device", "Medical devices")]
CLASSES = {"Class I": "Class I: a dangerous product that could cause serious health problems or death.",
           "Class II": "Class II: a product that might cause a temporary health problem, or a slight threat of a "
                       "serious one.",
           "Class III": "Class III: a product unlikely to cause any health problem, but that breaks FDA's labelling "
                        "or manufacturing rules."}


def today():
    """Today's date (a function, so the tests can set it)."""
    return datetime.date.today()


def months(first=FIRST_MONTH, last=None):
    """["2012-06", ..., this month], oldest first."""
    last = last or today().strftime("%Y-%m")
    y, m = map(int, first.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= last:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def api_get(path, params, cache=None):
    """One openFDA answer as JSON ({} when nothing matches: the API answers 404 then). The key, when the workflow
    has one (OPENFDA_API_KEY), is sent too; answers are not cached (they change every day)."""
    import urllib.error
    import build_textbooks as B
    params = dict(params)
    if os.environ.get("OPENFDA_API_KEY"):
        params["api_key"] = os.environ["OPENFDA_API_KEY"]
    url = f"{API}/{path}.json?" + urllib.parse.urlencode(params, safe="[]:+ ").replace(" ", "+")
    try:
        return json.loads(B.fetch(url, None))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        raise


def licence_still_open(answer):
    """True when an API answer still names openFDA's public-domain licence page."""
    return (answer.get("meta") or {}).get("license", "").rstrip("/") == LICENCE_URL.rstrip("/")


def month_range(month):
    """"2026-10" -> "[20261001 TO 20261031]" (the API's date search)."""
    y, m = map(int, month.split("-"))
    nxt = datetime.date(y + (m == 12), m % 12 + 1, 1) - datetime.timedelta(days=1)
    return f"[{y:04d}{m:02d}01 TO {nxt:%Y%m%d}]"


def month_records(kind, month, cache=None, limit=None):
    """Every enforcement record of one kind reported in one month (paged 1,000 at a time), and the last answer's
    meta (for the licence check and the date of the data)."""
    out, skip, meta = [], 0, {}
    while True:
        answer = api_get(f"{kind}/enforcement", {"search": f"report_date:{month_range(month)}", "limit": 1000,
                                                  "skip": skip, "sort": "report_date:asc"}, cache)
        meta = answer.get("meta") or meta
        rows = answer.get("results") or []
        out += rows
        total = ((meta.get("results") or {}).get("total")) or 0
        skip += len(rows)
        if not rows or skip >= total or skip >= 25000 or (limit and len(out) >= limit):
            return out, answer if answer else {"meta": meta}


def date_words(yyyymmdd):
    """"20261014" -> "2026-10-14" ("" when empty)."""
    s = (yyyymmdd or "").strip()
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if re.fullmatch(r"\d{8}", s) else s


def event_page(rows):
    """The body HTML of one recall event (its products share the firm and, mostly, the reason)."""
    import build_textbooks as B
    first = rows[0]
    out = [K.dl([("Recalling firm", first.get("recalling_firm")),
                 ("Address", ", ".join(x for x in (first.get("address_1"), first.get("city"), first.get("state"),
                                                   first.get("postal_code"), first.get("country")) if x)),
                 ("Classification", CLASSES.get(first.get("classification"), first.get("classification"))),
                 ("Status", first.get("status")), ("Who started it", first.get("voluntary_mandated")),
                 ("How the firm told its customers", first.get("initial_firm_notification")),
                 ("Recall started", date_words(first.get("recall_initiation_date"))),
                 ("Classified by FDA", date_words(first.get("center_classification_date"))),
                 ("In the Enforcement Report", date_words(first.get("report_date"))),
                 ("Closed", date_words(first.get("termination_date"))),
                 ("Where it was sold", first.get("distribution_pattern")),
                 ("FDA recall event number", first.get("event_id"))])]
    reasons = list(dict.fromkeys(r.get("reason_for_recall", "").strip() for r in rows if r.get("reason_for_recall")))
    out.append("<h2>Reason</h2>" + "".join(f"<p>{B.esc(x)}</p>" for x in reasons))
    out.append(f"<h2>Products ({len(rows)})</h2>")
    for r in rows:
        out.append(f"<h3>{B.esc(r.get('recall_number', ''))}</h3><p>{B.esc(r.get('product_description', ''))}</p>" +
                   K.dl([("Quantity", r.get("product_quantity")), ("Codes and lots", r.get("code_info")),
                         ("More codes", r.get("more_code_info"))]))
    return "\n".join(out)


def event_title(rows):
    """"Firm: product words (Class II)" for a recall event's page."""
    first = rows[0]
    product = re.split(r"[.;]| - ", first.get("product_description", "").strip())[0][:90].strip(" ,")
    more = f" and {len(rows) - 1} more" if len(rows) > 1 else ""
    return f"{first.get('recalling_firm', 'Recall')}: {product}{more} ({first.get('classification', '')})"


def announcements_page(cache=None):
    """The latest company recall announcements FDA posted (its RSS feed): titles, dates and links only."""
    import build_textbooks as B
    if not K.readable(RSS, cache):
        return None
    text = B.fetch(RSS, None)
    items = re.findall(r"<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>", text, re.S)
    if not items:
        return None
    lis = "".join(f'<li><a href="{B.esc(link.strip().replace("http://", "https://"))}">{B.esc(B.html.unescape(t))}'
                  f"</a> ({B.esc(d.strip())})</li>" for t, link, d in items)
    body = ("<p>The latest recall announcements that companies issued and FDA posted on fda.gov. Only their titles, "
            "dates and links are here: the announcements are written by the companies. Open a link in a browser for "
            f"the whole text.</p><ul>{lis}</ul>")
    return B.Page("company-announcements", "Company recall announcements posted by FDA (latest)", body, 0,
                  "Company announcements")


def about_page():
    """The first page of every month: what the classes mean and how to use the book."""
    import build_textbooks as B
    body = ("<p>Each page is one recall event from FDA's weekly Enforcement Report: the products a firm recalled for "
            "the same reason. Pages are in three parts: food and cosmetics, drugs, and medical devices.</p>"
            "<ul>" + "".join(f"<li>{B.esc(v)}</li>" for v in CLASSES.values()) + "</ul>"
            "<p>To check whether you have a recalled product, compare the product name, size and the lot or code "
            "numbers on its package with the \"Codes and lots\" of the recall. If it matches, stop using it and follow "
            "the firm's instructions, or ask the store, your pharmacist or your doctor.</p>"
            f"<p>{B.esc(DISCLAIMER)}</p>")
    return B.Page("about-recalls", "About these recalls", body, 0, "About")


def recalls_book(name, work, cache=None, left_out=None, limit=None):
    """One month of the Enforcement Report (name "recalls:2026-10")."""
    import build_textbooks as B
    month = name.split(":", 1)[1] if ":" in name else ""
    if month not in months():
        left_out.append({"title": name, "reason": f"Not a month from {FIRST_MONTH} to this month."})
        return None
    words = datetime.date(*map(int, month.split("-")), 1).strftime("%B %Y")
    book = K.new_book(f"fda_recalls_{month.replace('-', '_')}", f"FDA recalls, {words}: food, drugs and devices",
                      "Recalls (food, drugs, medical devices)", GROUP, PUBLISHER, K.CC0, LICENCE_URL,
                      "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts",
                      f"Every recall of food and cosmetics, drugs and medical devices that FDA classified and put in "
                      f"its Enforcement Report in {words}, one page per recall event: the firm, the reason, the class, "
                      "the products with their codes and lots, where they were sold and the status.", NOTICE,
                      changes="each recall's record made into a web page")
    book.pages.append(about_page())
    newest, paths = "", set()
    for kind, unit in KINDS:
        rows, answer = month_records(kind, month, cache, limit)
        if (answer.get("meta") or {}).get("license") is not None or rows:
            if not licence_still_open(answer):
                left_out.append({"title": book.title, "reason": "openFDA's answer no longer names its public-domain "
                                 "licence page."})
                return None
        newest = max(newest, (answer.get("meta") or {}).get("last_updated", ""))
        events = {}
        for r in rows:
            events.setdefault(r.get("event_id") or r.get("recall_number"), []).append(r)
        for event_id, ev in sorted(events.items(), key=lambda kv: (kv[1][0].get("recalling_firm", "").lower(),
                                                                    kv[0])):
            path = B.slug(f"{kind}-{event_id}", 40)
            while path in paths:
                path += "-2"
            paths.add(path)
            book.pages.append(B.Page(path, event_title(ev), event_page(ev), 0, unit))
        book.originals.append({"url": f"{API}/{kind}/enforcement.json?search=report_date:"
                                      f"{month_range(month).replace(' ', '+')}", "kind": "json"})
    if current(f"fda:{name}"):
        page = announcements_page(cache)
        if page:
            book.pages.append(page)
            book.originals.append({"url": RSS, "kind": "xml"})
    book.published = newest[:10] if current(f"fda:{name}") else (month if not newest else newest[:10])
    book.version = f"openFDA enforcement data updated {newest}" if newest else ""
    return book


def recalls_sign(name):
    """A past month's sign: how many of its recalls are in each status and class, by kind (a recall closed or
    reclassified changes it)."""
    month = name.split(":", 1)[1]
    parts = []
    for kind, _unit in KINDS:
        for field in ("status.exact", "classification.exact"):
            answer = api_get(f"{kind}/enforcement", {"search": f"report_date:{month_range(month)}", "count": field})
            parts.append(sorted((r["term"], r["count"]) for r in answer.get("results") or []))
    return K.sha(parts)


def shortages_book(name, work, cache=None, left_out=None, limit=None):
    """The current drug shortage list, one page per medicine (its packages, availability, reason and contact)."""
    import build_textbooks as B
    rows, skip, answer = [], 0, {}
    while True:
        answer = api_get("drug/shortages", {"limit": 1000, "skip": skip}, cache)
        if not licence_still_open(answer):
            left_out.append({"title": "FDA drug shortages", "reason": "openFDA's answer no longer names its "
                             "public-domain licence page."})
            return None
        got = answer.get("results") or []
        rows += got
        skip += len(got)
        if not got or skip >= answer["meta"]["results"]["total"] or (limit and len(rows) >= limit):
            break
    updated = answer["meta"].get("last_updated", "")
    book = K.new_book("fda_drug_shortages", "FDA drug shortages (current list)", "Drug shortages", GROUP, PUBLISHER,
                      K.CC0, LICENCE_URL, "https://dps.fda.gov/drugshortages",
                      "The FDA's current list of drug shortages: one page per medicine with each package's "
                      "availability (available, limited, unavailable), the reason for the shortage, the expected "
                      "date it ends where given, the therapeutic category and the company's contact.", NOTICE,
                      changes="each shortage record made into a web page")
    book.published, book.version = updated, f"openFDA drug shortages updated {updated}"
    book.originals.append({"url": f"{API}/drug/shortages.json", "kind": "json"})
    medicines = {}
    for r in rows:
        medicines.setdefault((r.get("generic_name") or "Unnamed").strip(), []).append(r)
    book.pages.append(B.Page("about-shortages", "About the drug shortage list",
                             "<p>One page per medicine in shortage, in alphabetical order. Each package (its NDC "
                             "number) has its own availability. Ask your pharmacist about another strength, form or "
                             f"medicine.</p><p>{B.esc(DISCLAIMER)}</p>", 0, "About"))
    paths = set()
    for med, recs in sorted(medicines.items(), key=lambda kv: kv[0].lower()):
        first = recs[0]
        cats = first.get("therapeutic_category") or []
        out = [K.dl([("Status", first.get("status")),
                     ("Therapeutic category", ", ".join(cats) if isinstance(cats, list) else cats),
                     ("First posted", first.get("initial_posting_date")), ("Last updated", first.get("update_date")),
                     ("Reason", first.get("shortage_reason")), ("Company contact", first.get("contact_info"))])]
        table = [(r.get("package_ndc", ""), r.get("presentation", "") or r.get("dosage_form", ""),
                  r.get("company_name", ""), r.get("availability", ""), r.get("related_info", "") or "")
                 for r in recs]
        out.append("<h2>Packages</h2>" + K.rows_table(table, ("NDC", "Presentation", "Company", "Availability",
                                                              "More information")))
        path = B.slug(med, 60)
        while path in paths:
            path += "-2"
        paths.add(path)
        book.pages.append(B.Page(path, med[:1].upper() + med[1:],
                                 "\n".join(out), 0, med[:1].upper() if med[:1].isalpha() else "#"))
    return book


def current(key):
    """True for the keys the daily refresh rebuilds under one monthly name: this month's recalls and the shortages."""
    return key in daily_keys()


def daily_keys():
    """This month's recalls and the drug shortages (the daily refresh)."""
    return [f"fda:recalls:{today():%Y-%m}", "fda:shortages"]


COLLECTION = K.Collection(
    "fda", GROUP, current=current,
    makers={"recalls": (recalls_book, recalls_sign), "shortages": (shortages_book, lambda name: "")},
    pieces={"recalls": lambda: months()},
    words={"fda-recalls": lambda: [f"fda:recalls:{m}" for m in months()[-24:]] + ["fda:shortages"],
           "recalls-all": lambda: [f"fda:recalls:{m}" for m in months()] + ["fda:shortages"]})

GROUPS = {}
LICENCE_LINES = {
    "openfda_recalls_shortages": "api.fda.gov answers carry \"license\": \"https://open.fda.gov/license/\" (checked at "
                                 "every build): openFDA content and data are public domain with a CC0 1.0 dedication. "
                                 "api.fda.gov has no robots.txt (404: no rules); without a key it allows 1,000 "
                                 "requests a day per address. open.fda.gov and download.open.fda.gov answer programs "
                                 "\"Access Denied\" (robots.txt included), so the bulk files and the terms page are not "
                                 "read. The recall RSS feed is read only for titles and links (www.fda.gov robots.txt "
                                 "allows it, Crawl-delay 30).",
}
NOT_INCLUDED = [
    ("openFDA bulk downloads (download.open.fda.gov) and openFDA's terms page", "download.open.fda.gov and "
     "open.fda.gov answer programs with \"Access Denied\" (robots.txt included, checked 2026-11-22); the same data are "
     "read through the API instead. Index: https://open.fda.gov/data/downloads/"),
    ("Text of company recall announcements (fda.gov press releases)", "Only their titles, dates and links are kept: "
     "they are written by the companies, not FDA, so FDA's public-domain statement may not cover them. Index: "
     "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
