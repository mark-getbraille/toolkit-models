"""MONEY, WORK AND BUSINESS for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists
the ready-made pack built in packs/money_work_packs.py (group "permissive"; the kit downloads it with prepare_pack)
and the sources looked at and left out, with the reason (MONEY_WORK_NOT_INCLUDED):
  synthetic_pay_documents  computer-made SPECIMEN pay stubs and W-2-like wage and tax statements (made-up people and
                           employers, Social Security numbers beginning 000 and employer numbers beginning 00, which
                           are never issued; never usable as real documents).

Tax answers end with "General information, not tax or legal advice; check the current rules or ask a professional."
Topic: documents (Documents, maps and signs). Picture-making (MONEY_WORK_PICTURE_MAKING_OK): none (a model must never
learn to draw convincing pay or tax documents).

    python -c "import sources, money_work_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

MONEY_WORK_SOURCES = [
    Source("synthetic_pay_documents", "Pay stubs and W-2 wage and tax statements, computer-made SPECIMEN examples with "
                                      "made-up names and amounts: gross and net pay, hours, deductions and the "
                                      "year's totals (synthetic, ready-made pack)",
           "CC0 (drawn by packs/money_work_packs.py from a fixed seed; made-up people and employers, impossible "
           "numbers, marked SPECIMEN)", "Computer-made by the kit's makers (packs/money_work_packs.py)", "permissive",
           2500, 25, prepare_pack, "about 380 MB"),
]

MONEY_WORK_PICTURE_MAKING_OK = set()

MONEY_WORK_NOT_INCLUDED = {
    "Real pay stubs, W-2s and tax forms filled in (photo sites, receipt datasets)": "They carry real people's "
        "names, numbers and pay; only computer-made SPECIMEN examples are used.",
    "Banknotes, coins, bills and statements": "Already in the currency, money and synthetic_bills packs.",
}
