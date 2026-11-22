"""Voting and housing rights for the reference library (the owner's request of 2026-11-22). Keys: civic (every
book), civic:<name>.

What this module builds, in plain words, each IN FULL:
  - the US Election Assistance Commission's pages for voters: voting accessibility (your rights as a voter with a
    disability, accessible voting machines, help at the polls), registering and voting in your state, the National
    Mail Voter Registration Form, voting for the first time, voter questions and answers, presidential elections and
    election security;
  - fair housing: the Department of Justice's guide to the Fair Housing Act, and the two joint statements of HUD and
    the Department of Justice that explain the rules for people with disabilities: "Reasonable Accommodations under
    the Fair Housing Act" (2004) and "Reasonable Modifications under the Fair Housing Act" (2008), whole.
USA.gov's housing help pages (tenant rights, eviction, rental programmes) are in gov_help.py (help:usa_gov).

Not built: Vote.gov (its robots.txt says "ai-train=no" and shuts out ClaudeBot) and HUD's web pages (they come to
programs with their main text empty, as before; only the two PDFs above could be read), link-only in NOT_INCLUDED.

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build). eac.gov, justice.gov and hud.gov allow the pages and files in robots.txt; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/civic_help.py civic:eac_voters --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "law"
NOTICE = K.NOT_LEGAL_ADVICE

GUIDES = [
    K.guide(GROUP, "eac_voters", "Voting: the Election Assistance Commission's guide for voters, with accessible "
            "voting", "Voting and elections", "US Election Assistance Commission (EAC)", "https://www.eac.gov/voters",
            r"^https://www\.eac\.gov/voters(/[a-z0-9-]+)*$",
            "The EAC's pages for voters: voting accessibility (the rights of voters with disabilities, accessible "
            "voting systems, assistance at the polls, curbside voting), registering and voting in your state, the "
            "National Mail Voter Registration Form, voting 101 for new voters, voter questions and answers, "
            "presidential elections, election security and national contacts.",
            "A work of the US Election Assistance Commission (public domain). Election rules and deadlines differ by "
            "state: check with your state or local election office.", depth=2,
            follow=r"^https://www\.eac\.gov/voters/[a-z0-9-]+$", limit=80),
    K.guide(GROUP, "doj_fair_housing", "The Fair Housing Act (US Department of Justice)", "Fair housing",
            "Civil Rights Division, US Department of Justice", "https://www.justice.gov/crt/fair-housing-act-1",
            r"^https://www\.justice\.gov/crt/(fair-housing-act-1|housing-and-civil-enforcement-section|"
            r"fair-housing-[a-z0-9-]+|the-fair-housing-act-[a-z0-9-]+)$",
            "The Department of Justice's guide to the Fair Housing Act: who is protected (race, colour, religion, sex, "
            "national origin, familial status and disability), what is forbidden, the rules for people with "
            "disabilities (reasonable accommodations and modifications, accessible design), housing for older "
            "persons, and how to report housing discrimination.",
            "A work of the US Department of Justice (public domain). " + NOTICE, limit=20),
]

PDFS = [
    K.us_pdf(GROUP, name="hud_doj_reasonable_accommodations", title="Reasonable Accommodations under the Fair Housing "
             "Act: Joint Statement of HUD and the Department of Justice (2004)", subject="Fair housing and disability",
             publisher="US Department of Housing and Urban Development and US Department of Justice",
             description="The whole joint statement, in questions and answers: who is protected, what a reasonable "
                         "accommodation is (a change to a rule, policy or service, such as an assistance animal or a "
                         "reserved parking space), how to ask, what a housing provider may ask about a disability, "
                         "when a request may be refused, and how to file a complaint.",
             pdf="https://www.hud.gov/sites/documents/huddojstatement.pdf", page="https://www.hud.gov/",
             published="2004-05-17", version="Joint Statement of 17 May 2004",
             notice="A work of HUD and the Department of Justice (public domain). HUD has issued later guidance on "
                    "assistance animals (2020). " + NOTICE),
    K.us_pdf(GROUP, name="hud_doj_reasonable_modifications", title="Reasonable Modifications under the Fair Housing "
             "Act: Joint Statement of HUD and the Department of Justice (2008)", subject="Fair housing and disability",
             publisher="US Department of Housing and Urban Development and US Department of Justice",
             description="The whole joint statement, in questions and answers: what a reasonable modification is (a "
                         "physical change to a home, such as a ramp, grab bars or a wider door), who pays, what a "
                         "housing provider may ask, restoring the home when you move, and how to file a complaint.",
             pdf="https://www.hud.gov/sites/documents/reasonable_modifications_mar08.pdf",
             page="https://www.hud.gov/", published="2008-03-05", version="Joint Statement of 5 March 2008",
             notice="A work of HUD and the Department of Justice (public domain). " + NOTICE),
]

COLLECTION = K.Collection("civic", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"civic": lambda: ["civic:eac_voters", "civic:doj_fair_housing",
                                                   "civic:hud_doj_reasonable_accommodations",
                                                   "civic:hud_doj_reasonable_modifications"]})

GROUPS = {}
LICENCE_LINES = {
    "eac_doj_hud": "eac.gov, justice.gov and hud.gov: works of the US government (17 U.S.C. 105, checked on "
                   "govinfo.gov's policies page at every build). Their robots.txt files allow the pages and files "
                   "read; no AI rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("Vote.gov", "Its robots.txt says \"Content-Signal: ai-train=no\" and shuts out ClaudeBot (checked 2026-11-22). "
     "Link-only for the personal assistant. Index: https://vote.gov/"),
    ("HUD's fair housing and reasonable accommodation web pages (hud.gov)", "They come to programs with their main "
     "text empty (only the page frame, checked again 2026-11-22), so they cannot be read; the two HUD and DOJ joint "
     "statements are built from their PDFs instead, and USA.gov's tenant rights pages are in help:usa_gov. Index: "
     "https://www.hud.gov/program_offices/fair_housing_equal_opp"),
    ("HUD's 2020 assistance animals notice (FHEO-2020-01) and other HUD PDFs", "Their old addresses no longer answer "
     "(404) and HUD's pages that list the new ones are empty to programs. Link-only. Index: "
     "https://www.hud.gov/program_offices/fair_housing_equal_opp/assistance_animals"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
