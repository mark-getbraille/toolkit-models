"""FILLED-IN GOVERNMENT FORMS for the Picture Model Training Kit (the owner's request of 2026-11-22: government forms
with their instructions). This file lists the ready-made pack built in packs/gov_forms_packs.py (group "permissive";
the kit downloads it with prepare_pack) and what was left out, with the reason (GOV_FORMS_NOT_INCLUDED):
  synthetic_gov_forms  computer-made SPECIMEN filled-in forms laid out like the IRS Form W-4, W-9 and 1099-NEC and
                       the SSA's Form SS-5 (made-up people and businesses, Social Security numbers beginning 000 and
                       employer numbers beginning 00, which are never issued; never usable as real forms).

The blank official forms are the us_federal_forms pack; the forms with their instructions are reference books
(textbooks/gov_forms.py, form:). Tax answers end with "General information, not tax or legal advice; check the
current rules or ask a professional." Topic: money (Money and paperwork). Picture-making
(GOV_FORMS_PICTURE_MAKING_OK): none (a model must never learn to draw convincing government forms).

    python -c "import sources, gov_forms_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

GOV_FORMS_SOURCES = [
    Source("synthetic_gov_forms", "Filled-in government forms (W-4, W-9, 1099-NEC, SS-5), computer-made SPECIMEN "
                                  "examples with made-up names and amounts: what is written in each box "
                                  "(synthetic, ready-made pack)",
           "CC0 (drawn by packs/gov_forms_packs.py from a fixed seed; made-up people and businesses, impossible "
           "numbers, marked SPECIMEN)", "Computer-made by the kit's makers (packs/gov_forms_packs.py)", "permissive",
           2000, 25, prepare_pack, "about 300 MB"),
]

GOV_FORMS_PICTURE_MAKING_OK = set()

GOV_FORMS_NOT_INCLUDED = {
    "Real filled-in tax and benefit forms (photo sites, form datasets)": "They carry real people's names, numbers "
        "and income; only computer-made SPECIMEN examples are used.",
    "SSA and USCIS blank forms as pictures": "ssa.gov and uscis.gov refuse programs (403, checked 2026-11-22); the "
        "IRS, Medicare, VA and OPM blank forms are in the us_federal_forms pack.",
}
