# Toolkit models

Converted AI models that the Digital Accessibility Toolkit (GetBraille.com) downloads the first time you use them.
This repository holds only the model files, the list of models and the script that converts them. It has none of
the program's code.

## Where the files are

The files are in the release **engine-models** of this repository. You never need to download them by hand: the
toolkit downloads the one it needs, checks it and unpacks it. A file bigger than 2 GB is published in numbered parts
(`name.zip.001`, `name.zip.002` and so on). The toolkit joins the parts and checks the SHA-256 of the whole zip.

## The models

All of them are 4-bit (int4) conversions of Qwen3 and Qwen3-VL models from huihui-ai. huihui-ai "abliterated" these
models, which means it removed their refusals. **They have no content filter**, so they will answer requests that
other models refuse. Use them responsibly.

| Key | Model | Engine | Converted from |
| --- | --- | --- | --- |
| ort-qwen3-4b-abliterated | Qwen3 4B, text | ONNX Runtime GenAI (DirectML graphics card, or processor) | [huihui-ai/Huihui-Qwen3-4B-Instruct-2507-abliterated](https://huggingface.co/huihui-ai/Huihui-Qwen3-4B-Instruct-2507-abliterated) |
| ort-qwen3-8b-abliterated | Qwen3 8B, text | ONNX Runtime GenAI (DirectML graphics card, or processor) | [huihui-ai/Huihui-Qwen3-8B-abliterated-v2](https://huggingface.co/huihui-ai/Huihui-Qwen3-8B-abliterated-v2) |
| ov-qwen3-4b-abliterated | Qwen3 4B, text | OpenVINO (Intel graphics, processor, NPU) | [huihui-ai/Huihui-Qwen3-4B-Instruct-2507-abliterated](https://huggingface.co/huihui-ai/Huihui-Qwen3-4B-Instruct-2507-abliterated) |
| ov-qwen3-8b-abliterated | Qwen3 8B, text | OpenVINO (Intel graphics, processor, NPU) | [huihui-ai/Huihui-Qwen3-8B-abliterated-v2](https://huggingface.co/huihui-ai/Huihui-Qwen3-8B-abliterated-v2) |
| ov-qwen3vl-4b-abliterated | Qwen3-VL 4B, pictures and text | OpenVINO (Intel graphics, processor) | [huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated](https://huggingface.co/huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated) |
| ov-qwen3vl-8b-abliterated | Qwen3-VL 8B, pictures and text | OpenVINO (Intel graphics, processor) | [huihui-ai/Huihui-Qwen3-VL-8B-Instruct-abliterated](https://huggingface.co/huihui-ai/Huihui-Qwen3-VL-8B-Instruct-abliterated) |

The exact source commit of each model is in `plan.json`.

### Translation models

79 translation models for the toolkit's offline translation, converted to CTranslate2 with 8-bit (int8) weights:

- 77 OPUS-MT models (keys `opus-mt-...`) by Helsinki-NLP, University of Helsinki
  ([huggingface.co/Helsinki-NLP](https://huggingface.co/Helsinki-NLP)), each for one pair of languages or one
  family of languages, into or out of English;
- MADLAD-400 3B and 7B (keys `madlad400-3b`, `madlad400-7b`) by Google
  ([google/madlad400-3b-mt](https://huggingface.co/google/madlad400-3b-mt),
  [google/madlad400-7b-mt](https://huggingface.co/google/madlad400-7b-mt)), about 400 languages in any direction.

Each zip also holds the original model's `README.md`, which names its authors, and the original SentencePiece files.

## Licence

The Qwen3 and Qwen3-VL models are under the **Apache License 2.0**, the licence of Qwen3 and Qwen3-VL (Alibaba
Cloud) and of huihui-ai's versions. MADLAD-400 is under the Apache License 2.0. Each OPUS-MT model keeps its own
licence: Apache License 2.0, or **CC BY 4.0** (https://creativecommons.org/licenses/by/4.0/; the authors are
Helsinki-NLP, University of Helsinki, OPUS-MT). The licence of each is in the toolkit's licence list and in the
original model's page. The full text is in [LICENSE](LICENSE). See [NOTICE](NOTICE) for what was changed. The
conversion script `convert_models.py` is also under the Apache License 2.0.

## How the models are made

The workflow `.github/workflows/convert.yml` converts each model and uploads it:

1. download the original model at its pinned commit;
2. convert it with `onnxruntime_genai.models.builder` or `optimum-cli export openvino`, with 4-bit weights, or, for
   a translation model, with CTranslate2's `ct2-transformers-converter`, with 8-bit weights;
3. zip it, then record its size and SHA-256.

The workflow runs when someone starts it from the Actions page, or when `convert-request.txt` changes on main.
That file lists model keys separated by commas, or `all`.

`plan.json` and `convert_models.py` are copied here from the toolkit by `python tools/convert_models.py --export`.
Change them there, not here.

## Picture Model Training Kit

`training-kit/` teaches the picture model (Qwen3-VL abliterated) to describe pictures the way a blind reader needs,
on your own NVIDIA graphics card. It trains a small add-on (a LoRA adapter) on DOCCI and VizWiz Captions (both CC BY
4.0) and tests the model before and after. Download it from the release **training-kit**, unpack it, and read
`READ ME FIRST.txt`. A trained add-on is published here only if its test shows it describes better.

## Open textbooks

The release **textbooks** holds open textbooks and reference works as ZIM files (the offline library format of
Kiwix), one file per book, and `textbooks.json`, the list the Digital Accessibility Toolkit reads (Offline libraries,
Get more, collection "Textbooks"). Each entry has the book's id, title, subject, level (school, college or
reference), publisher and credit, country, licence (non-commercial ones are marked "not for commercial use"),
language, size, SHA-256, number of pages, date (when the file was made), `published` (when the publisher published or
last revised the work: `YYYY-MM-DD`, `YYYY-MM` or `YYYY`, empty when the source does not say; the toolkit ranks newer
works higher), `region` (the state or province a law or guide applies to), and the official address of the
publisher's original PDF (and EPUB) when there is one, and `originals`, every original file and page with its
licence and whether it may be downloaded (see "Originals" below). `groups` maps each group key to the collection
name. The original PDFs are never copied here; the toolkit downloads them from the publisher.

The files are ordinary ZIM files, so the free Kiwix apps (Windows, Android, iOS, kiwix-serve) open them too.

What is built (`textbooks/sources.py` lists every source, the licence lines that were checked, and what was left out
and why):

- **OpenStax** (Rice University) textbooks, from the openstax/osbooks-* repositories on GitHub. Each book's licence
  is read from its own collection file every time it is built: some are CC BY 4.0, many are now CC BY-NC-SA 4.0
  (shown as "not for commercial use"). Retired editions are left out.
- **Siyavula** (South Africa) mathematics, physical sciences and natural sciences school textbooks, CC BY 4.0, from
  Siyavula's online reader (allowed by its robots.txt); the books are named by subject and grade, crediting
  Siyavula Education (its "Everything Maths" and "Everything Science" names are its trademarks and are not used).
- **Reference works** of international bodies (the WHO's Model List of Essential Medicines, the World Bank's World
  Development Report 2024, FAO's State of Food and Agriculture 2024), from their open repositories, with the licence
  of each record (CC BY 3.0 IGO, or CC BY-NC-SA 3.0 IGO).
- **Reference, non-profits** (group `nonprofit`): openly licensed guides of non-profit organisations, from their
  web pages: the Electronic Frontier Foundation's Surveillance Self-Defense (CC BY 4.0), People's Law School's
  plain-language legal information for British Columbia (CC BY-NC-SA 4.0, text only) and the W3C Web Accessibility
  Initiative's Curricula on Web Accessibility (CC BY 4.0). Each guide's licence page is checked at every build, and a
  page without the guide's licence line is left out.
- **Reference, field manuals** (group `fieldmanual`): US military manuals on survival, first aid, map reading,
  rigging, field sanitation, cold weather and mountaineering, US government works (public domain), only when their
  own front matter says "Approved for public release; distribution is unlimited" (Distribution Statement A) and
  shows no restricted marking; chapters about weapons or tactics are left out. Copies from the Internet Archive
  (armypubs.army.mil's robots.txt shuts out automated readers). Also two UK documents under the Open Government
  Licence v3.0 from gov.uk: the Maritime and Coastguard Agency's Survival at Sea notice (MSN 1560) and the Ministry
  of Defence's first-aid chapter of JSP 375. Since November 2026 also two Army field hygiene manuals (FM 21-10, TC
  4-02.3), under the same Distribution Statement A check (`textbooks/reference_more.py`).
- **Courses** (group `course`): US Navy nonresident training courses with Distribution Statement A: sixteen modules
  of the Navy Electricity and Electronics Training Series (NEETS), Basic Machines, Culinary Specialist and Hospital
  Corpsman (US government works), and six more Navy rate training manuals (Military Requirements for Petty Officer
  Third Class, Quartermaster, Construction Mechanic, Equipment Operator, Alternating Current and Transformers,
  Opticalman). PDFs that are scans without words are refused.
- **Reference, governments** (group `government`): Government of Alberta publications under the Open Government
  Licence - Alberta (the Driver's Guide, seniors' safety guides, power-outage preparedness), the newest official PDF;
  the FAA's aviation handbooks (Pilot's Handbook of Aeronautical Knowledge, Airplane Flying, Instrument Flying,
  Aviation Weather, the three Aviation Maintenance Technician handbooks and more) and NIST Handbooks 44, 130 and 133
  (US government works).
- **Reference, laws and rights** (group `law`), one book per law so only the wanted ones are downloaded: US Code
  chapters (ADA, Rehabilitation Act, IDEA, Fair Housing Act, Consumer Credit Protection Act, Social Security Titles II
  and XVI) and Code of Federal Regulations parts (air travel 14 CFR 382, ADA rules 28 CFR 35 and 36 and 29 CFR 1630,
  fair housing 24 CFR 100, transportation 49 CFR 37, telecommunications accessibility 47 CFR 6, 7, 14 and 64 subpart
  F, Section 508 standards 36 CFR 1194, IDEA rules 34 CFR 300, food labeling 21 CFR 101) from govinfo.gov's newest
  annual editions (public domain; key `laws-more` adds larger ones such as Regulation Z and the SSA rules), the FTC's
  consumer rules (Funeral Rule, warranties, care labels, Cooling-Off Rule, Telemarketing Sales Rule), and with
  `laws-more` drug labelling (21 CFR 201), Medicare Parts B and D (42 CFR 410, 423) and the FMCSA driver rules (49 CFR
  390-396); the Social Security Act's Titles II, XVI, XVIII and XIX as amended (govinfo statute compilations); Canada's
  Accessible Canada Act and Regulations, Canadian Human Rights Act, Employment Equity Act and accessible
  transportation regulations from Justice Laws (Reproduction of Federal Law Order; marked "not the official
  version"); and the UK's Equality Act 2010, Consumer Rights Act 2015, Care Act 2014 and Landlord and Tenant Act 1985
  from legislation.gov.uk (Open Government Licence v3.0). One page per section (or part), listed under its subpart,
  part or chapter; editorial notes left out.
- **Reference, consumer and money** (`consumer`), **health and safety** (`health`), **disability and
  accessibility** (`disability`) and **science and nature** (`science`): US government guides in the public domain
  (Ask CFPB, Section508.gov, ADA.gov, NIDDK health information, FDA Consumer Updates, the National Cancer Institute's
  "About cancer", USGS This Dynamic Earth) and PDFs (IRS Publications 17, 554 and 907, Medicare & You, the 2010 ADA
  Standards), and UK guides under the Open Government Licence (the NHS Health A to Z, GOV.UK's guides for disabled
  people and on benefits, the Highway Code). Each site's copyright policy is checked at every build.
- A "NoDerivatives" work only kept whole with its text unchanged (format conversion only, which CC licences allow):
  every page then says "Converted to an accessible format; the text is unchanged." (W3C WAI documents, the ICEB Rules
  of Unified English Braille, KFF Health News, The Conversation).
- **Publications** (`textbooks/periodicals.py`, keys `publications` and `pub:...`): government reports, open-access
  journal articles, open-licensed news, magazines, parliamentary debates and history, each source split into pieces
  (years, decades, topics, editions, volumes, or state and decade), every item with its date, in its own release
  (`publications-<source>`), listed in `textbooks.json` with `complete` (false while a piece is still being
  collected) and `pieces_done`. Added in November 2026 (`textbooks/publications_more.py`, asked for by key, not in
  the hourly backfill): Government of Canada publications under the Open Government Licence - Canada
  (`pub:canada_ogl`: health, transport, veterans, law; the PDF documents only, as the canada.ca web pages allow only
  non-commercial use), GAO reports by year (`pub:gao_reports:1989` to `2008`), the United States Government Manual
  (`pub:us_government_manual`), ERIC full texts whose own text states public domain or an open Creative Commons
  licence (`pub:eric_open`: vision, braille, assistive technology, deafblindness, adult education), GOV.UK guides
  (`pub:govuk_guides`: carers, pensions, housing, tax and debt, driving), UK drug, device and product safety alerts
  (`pub:uk_safety_alerts:drug-2026`) and USDA Farmers' Bulletins by decade (`pub:usda_farmers_bulletins:1940s`, with
  a notice that old advice can be unsafe). The UK National Archives' teaching resources are a guide
  (`guide:uk_national_archives_teaching_resources`).
- **Blogs and online magazines** (`textbooks/blogs.py`, added November 2026): general-interest blogs with open
  licences, one book per year (`pub:pluralistic:2025`; a month for a small build, `pub:pluralistic:2025-10`), every post
  whole with its date, author and address; the current year in the daily refresh, every earlier year in the hourly
  backfill back to the blog's first post: Cory Doctorow's Pluralistic (CC BY 4.0, serialized fiction left out), the
  Creative Commons blog (CC BY 4.0), Waging Nonviolence (CC BY 4.0), Wikimedia's Diff (CC BY-SA 4.0), EFF's Deeplinks
  blog (CC BY 4.0) and the UK Government Digital Service's accessibility blog (Open Government Licence, group
  "disability"). A site whose robots.txt shuts out AI readers or says `ai-train=no` is not read (Boing Boing,
  Techdirt, MetaFilter and others), nor one whose terms forbid taking stories wholesale or automatically
  (ProPublica, The 19th, Common Dreams); those and the copyrighted ones (Hackaday, Make:, Wired, Ars Technica ...) are
  in `periodicals.NOT_INCLUDED` with their feed address, for the Program Downloader (personal use only).
- **More WCAG and accessibility guides** (`textbooks/accessibility_guides.py`, group "disability", added November
  2026): from W3C, whole and unchanged, WCAG 2.1, Techniques for WCAG 2.2, the ARIA Authoring Practices Guide, How to
  Meet WCAG (Quick Reference), Easy Checks, Accessibility Fundamentals, Web Accessibility Laws & Policies, ATAG 2.0,
  UAAG 2.0, EPUB Accessibility 1.1 and WCAG2ICT (keys `nonprofit:w3c_...`); the US Access Board's Revised 508
  Standards, ADA and ABA Standards and Guide to the ADA Standards, the ICT Testing Baseline and the NLS reference
  guides (public domain); the GOV.UK Service Manual's accessibility pages (Open Government Licence); and the A11y
  Project (Apache License 2.0) (keys `guide:...`). Copyrighted guides (AAArdvark's "WCAG in Plain English", WebAIM,
  Deque, BANA, NFB, ACB ...) are in `sources.NOT_INCLUDED` with their index address.
- **Medicines** (`textbooks/medications.py`, keys `medicines` and `med:...`): the official US labels of medicines,
  read from DailyMed (National Library of Medicine) through its web services: 14 books of prescription medicines
  and 7 of over-the-counter medicines (by first letter), and two of animal medicines (pets and horses; farm
  animals). One page per medicine by its generic name, brand names (US, and Canadian from Health Canada's Drug
  Product Database) leading to it, and each label in the same plain order: what it is for, how to take it,
  warnings (the boxed warning first), side effects, interactions, storage, pregnancy and breastfeeding, the patient
  leaflet (Medication Guide), then the rest of the label, in the label's own words. Every page says "Information,
  not medical advice: ask a pharmacist or doctor" (animals: "ask a veterinarian"). In their own release
  (`medicines`), rebuilt each month after DailyMed's monthly release, old versions kept.
- **School books, K-12** (key `k12`, group "School books (K-12)"): Illustrative Mathematics' student books for
  grades 6 to 8, Algebra 1, Geometry and Algebra 2 and its K-5 family materials (CC BY 4.0), Open Up HS Math (CC
  BY-NC 4.0, personal use only), the Utah State Board of Education's science books for kindergarten to high school
  (CC BY-NC-SA 3.0, personal use only), Siyavula (more grades) and OpenStax's high school books (keys `k12:<name>`,
  `pdf:utah_science_<grade>`); every book shows its grade level.
- **Open courses and personal-use courses** (`textbooks/courses.py`, keys `opencourses`, `personaluse`,
  `course:<source>` and `course:<source>:<piece>`): every LibreTexts book with an allowed licence (from its full
  PDF, split back into its pages, each with its own licence line), BCcampus' open textbooks from its Kolibri Studio
  channel, and, marked "personal use only", Khan Academy, CK-12 and EngageNY from their Kolibri Studio channels
  (Khan Academy is never read from its website), every MIT OpenCourseWare course from its offline zip, and Core
  Knowledge's free materials. Big sources are split into pieces so no build job takes more than 4 hours; each
  source has its own release (`libretexts-<library>`, `courses-bccampus`, `personal-...`). What was looked at and
  not built (SkillsCommons, the BCcampus and eCampusOntario sites, Open Course Library, OER Commons, Saylor,
  TED-Ed, OpenLearn ...) is in `courses.NOT_INCLUDED`, with the reason.

How the books are made accessible: one page per chapter and section with headings; an index page listing every unit,
chapter and section; every figure's number, the publisher's description of the picture and its caption as text
(pictures themselves only when the request asks for them); formulas as readable text; tables with captions;
teacher-only notes left out; and on every page the credit and licence.

The ZIM files are written by `textbooks/zimwrite.py`, our own writer made from the openZIM format description: no GPL
library (libzim) is used, not even in the build.

The workflow `.github/workflows/textbooks.yml` builds the books when someone starts it from the Actions page, or when
`textbooks/request.txt` changes on main (keys separated by commas, or `all`; also `nonprofit`, `fieldmanuals`,
`government`, `courses`, `guides`, `laws`, `laws-more`, `group:<group>` such as `group:health`, or one book such as
`law:us_code_ada`; `sources.expand_keys` lists them). `python -m pytest textbooks` tests the builder with a made-up book and a made-up website.

Each book keeps its own licence; the credit and licence are on its welcome page and in `textbooks.json`.

### Originals: the files each book and manual was made from (for the Program Downloader)

Every book in `textbooks.json` and every entry of every manual collection index has a field `originals`: the
publisher's own files and pages the book or entry was made from, with what may be done with each. The owner's
Program Downloader reads the two catalogues from the GitHub releases and downloads every original whose
`may_download` is `true` into `B:\Original sources`; the others are links the owner opens in a browser.

Where the catalogues are (release assets; the addresses always give the newest copy):

| What | Release | Asset name | Address |
| --- | --- | --- | --- |
| Books catalogue | `textbooks` | `textbooks.json` | https://github.com/mark-getbraille/toolkit-models/releases/download/textbooks/textbooks.json |
| Manuals catalogue | `manuals` | `manuals.json` | https://github.com/mark-getbraille/toolkit-models/releases/download/manuals/manuals.json |
| One manual collection's index | `manuals` | `manuals-<key>.<YYYY-MM-DD>.json.gz` (gzipped JSON) | the `url` of the newest entry of `manuals.json` `collections.<key>.versions` (or `RELEASE/` + `collections.<key>.file`) |

`textbooks.json` lists every book, including those whose ZIM file is in another release (`medicines`,
`libretexts-*`, `courses-*`, `personal-*`, `publications-*`): the book's `originals` are in its entry in
`textbooks.json` (`books[]`). `manuals.json` lists the collections (`collections.<key>`, with `original_count` and
`downloadable_count`); the manual records, each with its `originals`, are the `entries[]` of the collection's index
file.

Each item of `originals`:

| Field | Meaning |
| --- | --- |
| `url` | the original's own address at the publisher (never a copy in this repository) |
| `kind` | `pdf`, `epub`, `zip`, `html` (a web page), `csv`, `xml`, `json`, `txt`, `mp3`, `sqlite`, `jpg`, `png` ... |
| `size` | bytes, `0` when not known |
| `sha256` | the file's SHA-256 when the builder downloaded it, else `""` (a web page changes, so it has none) |
| `licence` | the licence or rights as shown to the owner ("CC BY 4.0", "CC BY-NC-SA 4.0, not for commercial use, personal use only", "a US government work (public domain)", "belongs to its maker ...") |
| `may_download` | `true` only when the licence allows copying AND the host's robots.txt (checked when the catalogue was built) and terms allow automated download; otherwise `false` |
| `why` | the reason in plain words, for both answers (for `false`: open the link in a browser) |

Notes for a downloader: personal-use originals (`licence` ending "personal use only") may be downloaded for the
owner's own use only. Books built before this field existed get it when the catalogue is merged; their robots.txt
answer may be "not checked" (so `may_download` is `false`) until the book is built again. The older fields
`original_pdf` and `original_epub` (`{url, size, sha256}`) stay for compatibility; they are also in `originals`.
Download one file at a time, with a pause between requests to the same site, and keep the `url` as given.

### Automatic updates, and where old versions are

The workflows also run on their own, on GitHub's schedule (times in UTC):

- **Daily news, 10:23**: the current pieces of the news sources are built again (Voice of America's recent stories
  and this year, VOA Learning English, Global Voices, NASA, KFF Health News, The Conversation, CRS reports, UK Hansard,
  Oireachtas debates, GOV.UK speeches, and this year of each blog). A news book keeps one file per month.
- **Backfill, every hour at :17**: the next older piece of any source, small and quick sources first (VOA radio
  scripts, Learning English, Milestones, FRUS, CRS, Amber Waves, KFF Health News, Global Voices, ...), then the big
  ones (VOA years, NASA, The Conversation, Hansard, historic newspapers), newest to oldest, one piece at a time.
  A piece too large for one run is published as far as it got with `"complete": false` and continued by the next
  run; VOA's are read by one job at a time.
- **Weekly update check, Sundays 09:41**: every other book's source is asked cheaply whether it changed (a
  repository's newest commit, an edition date, a PDF's checksum or server date, a sitemap's dates); only changed
  books are built again (`textbooks/updates.py`).
- **Manual collections, Wednesdays 09:53** (`.github/workflows/manuals.yml`): every collection is built again.

**Stop switches**: `textbooks/schedule.txt` (`daily`, `backfill`, `weekly`) and `manuals/schedule.txt` (`weekly`):
change `on` to `off` and commit to main; change it back to start again.

**Old versions are kept.** A book or manual collection that changed is published under a new name
(`<name>.<YYYY-MM-DD>.zim`, `manuals-<key>.<YYYY-MM-DD>.json.gz`) and the old file stays. `textbooks.json` and
`manuals.json` list, for each book or collection, `versions` (file, url, size, sha256, published, built,
change_note), newest first; the newest is also in the entry's own fields. A rebuild with the same text adds no
version. When a release nears GitHub's limit of 1,000 files, its oldest versions move to yearly archive releases
(`textbooks-archive-2026`, `publications-voa-archive-2026`, ...) and their addresses in the list follow.
