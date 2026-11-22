"""Money, banking, credit, debt and scams for the reference library (the owner's request of 2026-11-22). Keys: money
(every book), money:<name>.

What this module builds, in plain words, each IN FULL:
  - the Consumer Financial Protection Bureau's consumer tools: every page of its guides to bank accounts, credit
    cards, credit reports and scores, debt collection, mortgages and reverse mortgages, auto loans, student loans,
    payday loans, prepaid cards, money transfers, fraud and scams, retirement, managing someone else's money,
    disasters and emergencies, unexpected job loss and money as you grow, with the "Ask CFPB" answers those guides
    link to;
  - the CFPB's "Your Money, Your Goals" financial empowerment toolkit (the whole PDF: setting goals, saving,
    tracking income and spending, paying bills, credit, debt, choosing financial products, protecting your money);
  - the FDIC's consumer resource center and Money Smart: every page (deposit insurance, banking basics, getting a
    bank account, the Money Smart programmes for adults, older adults, young people and small businesses, consumer
    news and assistance).

Not built: the FTC's consumer advice and scam alerts (consumer.ftc.gov and ftc.gov answer programs "403
Forbidden", robots.txt included), link-only by year in NOT_INCLUDED.

Licences: CFPB and FDIC pages are works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's
policies page at every build). robots.txt of both allows the pages (FDIC asks a 1-second pause, which the builder
keeps); no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/money_help.py money:cfpb_consumer_tools --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "consumer"                         # "Reference, consumer and money"
CFPB = "https://www.consumerfinance.gov"
NOT_ADVICE = "General information, not financial or legal advice."
TOPICS = ("auto-loans|bank-accounts|credit-cards|credit-reports-and-scores|debt-collection|disasters-and-emergencies|"
          "financial-well-being|fraud|guide-to-filing-your-taxes|managing-someone-elses-money|military-financial-"
          "lifecycle|money-as-you-grow|money-transfers|mortgages|payday-loans|prepaid-cards|retirement|"
          "reverse-mortgages|student-loans|unexpected-job-loss|everyone-has-a-role|older-americans")

GUIDES = [
    K.guide(GROUP, "cfpb_consumer_tools", "Consumer Financial Protection Bureau: consumer guides and Ask CFPB",
            "Money, banking, credit and debt", "Consumer Financial Protection Bureau (CFPB)",
            f"{CFPB}/consumer-tools/",
            rf"^https://www\.consumerfinance\.gov/(consumer-tools/({TOPICS})(/[a-z0-9-]+)*|ask-cfpb/[a-z0-9-]+-en-"
            r"\d+)/?$",
            "Every page of the CFPB's consumer guides: bank accounts, credit cards, credit reports and scores, debt "
            "collection (your rights, sample letters), mortgages and reverse mortgages, auto loans, student loans, "
            "payday loans, prepaid cards, money transfers, fraud and scams, retirement, managing someone else's "
            "money, disasters and emergencies, unexpected job loss and money as you grow, with the Ask CFPB "
            "answers they link to.",
            "A work of the Consumer Financial Protection Bureau (public domain). " + NOT_ADVICE,
            depth=2, follow=rf"^https://www\.consumerfinance\.gov/consumer-tools/({TOPICS})(/[a-z0-9-]+)?/?$",
            units=[(r"/ask-cfpb/", "Ask CFPB answers")] +
                  [(rf"/consumer-tools/{t}", t.replace("-", " ").capitalize()) for t in TOPICS.split("|")],
            limit=700),
    K.guide(GROUP, "fdic_consumer", "FDIC consumer resource center and Money Smart", "Banking and money skills",
            "Federal Deposit Insurance Corporation (FDIC)", "https://www.fdic.gov/consumer-resource-center",
            r"^https://www\.fdic\.gov/(consumer-resource-center|resources/deposit-insurance)(/[a-z0-9-]+)+$",
            "Every page of the FDIC's consumer resource center: deposit insurance (is my money safe, what is "
            "covered), banking basics and getting a bank account, Money Smart for adults, older adults, young "
            "adults, young people and small businesses, FDIC Consumer News, consumer assistance and complaints, "
            "and youth savings.",
            "A work of the Federal Deposit Insurance Corporation (public domain). " + NOT_ADVICE,
            depth=2, follow=r"^https://www\.fdic\.gov/consumer-resource-center/[a-z0-9-]+$",
            units=[(r"money-smart", "Money Smart"), (r"consumer-news", "FDIC Consumer News"),
                   (r"deposit-insurance", "Deposit insurance"), (r".", "Consumer resources")], limit=300),
]

PDFS = [
    K.us_pdf(GROUP, name="cfpb_your_money_your_goals", title="Your Money, Your Goals: a financial empowerment toolkit "
             "(CFPB)", subject="Money management", publisher="Consumer Financial Protection Bureau (CFPB)",
             description="The CFPB's whole toolkit for people who help others with money, and for anyone: setting "
                         "goals, saving for emergencies and goals, tracking income and benefits, tracking spending, "
                         "paying bills, getting through tough months, dealing with debt, understanding credit reports "
                         "and scores, choosing financial products and services, and protecting your money, with its "
                         "worksheets and tools.",
             pdf="https://files.consumerfinance.gov/f/documents/cfpb_your-money-your-goals_financial-empowerment_"
                 "toolkit.pdf",
             page=f"{CFPB}/consumer-tools/educator-tools/your-money-your-goals/toolkit/",
             published="2018-11", version="Toolkit as posted by the CFPB (2018 edition, updated tools)",
             notice="A work of the Consumer Financial Protection Bureau (public domain). " + NOT_ADVICE),
]

COLLECTION = K.Collection("money", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"money": lambda: ["money:cfpb_consumer_tools", "money:cfpb_your_money_your_goals",
                                                   "money:fdic_consumer"]})

GROUPS = {}
LICENCE_LINES = {
    "cfpb_fdic": "consumerfinance.gov and fdic.gov: works of the US government (17 U.S.C. 105, checked on "
                 "govinfo.gov's policies page at every build). robots.txt: consumerfinance.gov \"User-agent: *\" "
                 "with only system folders disallowed; fdic.gov Crawl-delay 1; files.consumerfinance.gov has no "
                 "robots.txt; no AI rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("FTC consumer advice and scam alerts (consumer.ftc.gov), by year", "Public domain, but consumer.ftc.gov and "
     "www.ftc.gov answer programs \"403 Forbidden\" (robots.txt included, checked again 2026-11-22). Link-only for "
     "the personal assistant: the consumer alerts by year are at "
     "https://consumer.ftc.gov/consumer-alerts?field_date_value[min]=2026-01-01. Index: https://consumer.ftc.gov/"),
    ("Ask CFPB answers not linked from the consumer guides", "Ask CFPB has no list of all its answers for programs "
     "(its sitemap leaves them out); the answers the guides link to are built. Index: "
     "https://www.consumerfinance.gov/ask-cfpb/"),
    ("CFPB newsroom and blog archives", "Left out: news releases and blog posts, not guides. Index: "
     "https://www.consumerfinance.gov/about-us/blog/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
