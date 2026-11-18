# Where each picture collection goes

The owner's standing rule: every collection that is found is included, in the category its licence allows. None is
dropped only because of its licence.

| Category | Licences | How it is used |
|---|---|---|
| Open (ready-made packs, `packs/*.py`) | CC0, public domain, CC BY, ODC-By, CDLA-Permissive, MIT, Apache, BSD, open government licences that allow any use with credit | Built here and published in the release "training-data"; always used |
| Share-alike (`group="share-alike"`) | CC BY-SA, ODbL, GPL-style copyleft | Downloaded by the kit from the source; used only with the share-alike choice (Wikipedia option) |
| Non-commercial (`group="noncommercial"`) | CC BY-NC, BY-NC-SA, BY-NC-ND and other non-commercial terms | Downloaded by the kit from the source; personal-use box (Alt+Q); the result is personal use only |
| Research (`group="research"`) | research, academic or educational use only, or no stated terms | Downloaded by the kit from the source; personal-use box (Alt+Z) after agreeing to the terms; personal use only |
| Needing sign-up | any collection behind a login, form or signed agreement | Listed with its link in the kit's source files; the owner can get it and use the own-pictures folder |

Safety rules apply to every category:
- no sexual content;
- children only in everyday scenes, expressions, medical close-ups under the childhood-illness rules, and the birth
  context; never unclothed children elsewhere, never in nude art;
- adult-only for medical photos of people where ages are known;
- picture-making never learns from pictures of children, medical pictures, or the birth and childhood-illness
  collections;
- graphic scenes (war, disasters, injuries and death) are kept and described plainly from their records; their rows
  carry "content": "graphic" and are used only with the kit's graphic-scenes choice, never for picture-making;
  sexual violence, pictures whose focus is a dead or injured child, and torture or execution scenes (unless the
  record is documented evidence, such as the liberation of the camps) are always left out.
Every licence is checked at its source, and every picture keeps its credit.

## Pictures that need a description

A picture that passes every rule above and every check of its builder (licence, safety, a real photo, size, not a
repeat) but is dropped ONLY because its description is missing or poor is set aside instead of thrown away
(`build_packs.needs_description`): it goes into `needs-<key>.vN.zip` in the release "needs-description", never into
the pack. It keeps its pack's licence category, its credit, its marks ("child", "content": "graphic" or "medical")
and is never used for picture-making when it shows a child, graphic or medical content, or comes from a pack in the
kit's NOT_FOR_PICTURE_MAKING. NoDerivatives licences are never set aside (a new description is a change); a source
whose terms forbid copying its pictures gives address-only rows. Nothing set aside is trained on until a person
describes it and marks it checked (the zip opens in the kit as a review collection). Pictures whose safety or age
can only be judged from their words (medical, anatomy, nudes in art, children's rites) are never set aside.
