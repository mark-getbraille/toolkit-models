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
- no sexual content, except the two labelled collections of `adult_art_packs.py` (the owner's decision, November
  2026): museum_art_nudes (fine-art nudity, content "nudity") and erotic_art (sexual acts between adults in ART and
  ILLUSTRATION only, content "sexual", which makes a trained add-on personal use only). Both are describing only,
  never for picture-making. Hard limits, never relaxed: no photograph of a nude child; no artwork of any period
  showing a child in a sexual way (illegal in the UK, Canada and Australia whatever the medium); nothing sexual where
  any figure is or may be under 18 (in erotic_art any clear minor word leaves the item out; the adult phrases "young
  woman", "young man", "young couple", "maiden", "nymph" and "youthful" count as adult only outside Japanese works,
  where they often stand for wakashu or musume); no animals; no killing, torture or execution. erotic_art KEEPS works
  of sexual violence, no consent and restraint (the owner's decision, November 2026), said factually and tagged
  "theme" so a training can leave them out (train.py --without-sexual-violence). Photographs of nudity or sex are
  only in the kit's local, never-published training-kit/kit/adult_photo_review.py, and only when the institution's
  record documents that every person is an adult. Descriptions follow training-kit/HOW TO DESCRIBE SEXUAL CONTENT,
  NUDITY AND CONSENT.txt;
- children only in everyday scenes, expressions, medical close-ups under the childhood-illness rules, the birth
  context, and plainly non-sexual works of art in museum_art_nudes (Madonna and Child, putti: never a photograph,
  never with a sexual or romantic word, rows marked "child"); never unclothed children elsewhere;
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
