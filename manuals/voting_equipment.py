"""The collection "Accessible voting machines and ballot marking devices (manuals)" (category key voting_equipment):
the owner's request of 2026-11-22 for citizenship and civics. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia         the Internet Archive's manual collections, searched by the words in IA_WORDS (voting machines, ballot
             marking devices, ballot scanners);
  makers     the makers of the voting systems used in the US: by the owner's rule their own manuals are LINK-ONLY,
             for the person (or the personal assistant) to open in a browser or fetch with Program Downloader;
             nothing is read from their sites;
  documents  the Election Assistance Commission's Voluntary Voting System Guidelines (a US government work, given in
             FULL: the accessibility requirements every certified machine must meet) and its voters' pages (built in
             full in the reference library: civic:eac_voters).

The notice is said first (NOTICE): every polling place must have a way for blind voters to vote privately.
"""

NOTICE = ("Under the Help America Vote Act every polling place for federal elections must have at least one voting "
          "system that lets voters with disabilities, including blind voters, vote privately and independently. Ask "
          "a poll worker for the accessible machine and its audio ballot; you may also bring someone to help you.")

IA_WORDS = ["voting machine", "ballot marking", "ballot scanner"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="voting_equipment", prefix="ve", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="ess", maker="Election Systems & Software (ExpressVote)", type="ballot marking device",
         library="https://www.essvote.com/", site="essvote.com"),
    dict(key="hart", maker="Hart InterCivic (Verity)", type="ballot marking device",
         library="https://www.hartintercivic.com/", site="hartintercivic.com"),
    dict(key="dominion", maker="Dominion Voting Systems (ImageCast)", type="ballot marking device",
         library="https://www.dominionvoting.com/", site="dominionvoting.com"),
    dict(key="clear-ballot", maker="Clear Ballot (ClearAccess)", type="ballot marking device",
         library="https://clearballot.com/", site="clearballot.com"),
]]

DOCUMENTS = [
    dict(key="eac-vvsg", by="US Election Assistance Commission", product="voting systems",
         title="Voluntary Voting System Guidelines (VVSG), with the accessibility requirements (EAC)",
         url="https://www.eac.gov/voting-equipment/voluntary-voting-system-guidelines", type="voting machine",
         document="guide", access="full", rights="a US government work (public domain)",
         reason="a US government work; robots.txt allows this builder"),
]

GUIDANCE = [
    dict(title="Voting with a disability and the voter's guide (EAC; in the reference library: civic:eac_voters)",
         url="https://www.eac.gov/voters", by="the US Election Assistance Commission"),
]

CATEGORY = dict(
    name="Accessible voting machines and ballot marking devices (manuals)",
    description="Voting machines, accessible ballot marking devices with audio ballots, and ballot scanners: the "
                "Internet Archive's manuals, the makers' pages (links) and the Election Assistance Commission's "
                "Voluntary Voting System Guidelines.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, documents=DOCUMENTS, guidance=GUIDANCE, notice=NOTICE)
