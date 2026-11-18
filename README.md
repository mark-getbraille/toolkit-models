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
language, size, SHA-256, number of pages, date, and the official address of the publisher's original PDF (and EPUB)
when there is one. The original PDFs are never copied here; the toolkit downloads them from the publisher.

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
  of Defence's first-aid chapter of JSP 375.
- **Courses** (group `course`): US Navy nonresident training courses with Distribution Statement A: sixteen modules
  of the Navy Electricity and Electronics Training Series (NEETS), Basic Machines, Culinary Specialist and Hospital
  Corpsman (US government works). PDFs that are scans without words are refused.
- **Reference, governments** (group `government`): Government of Alberta publications under the Open Government
  Licence - Alberta (the Driver's Guide, seniors' safety guides, power-outage preparedness), the newest official PDF.
- Never a "NoDerivatives" work: a ZIM file is an adaptation (pages rewritten as web pages, formulas as text).

How the books are made accessible: one page per chapter and section with headings; an index page listing every unit,
chapter and section; every figure's number, the publisher's description of the picture and its caption as text
(pictures themselves only when the request asks for them); formulas as readable text; tables with captions;
teacher-only notes left out; and on every page the credit and licence.

The ZIM files are written by `textbooks/zimwrite.py`, our own writer made from the openZIM format description: no GPL
library (libzim) is used, not even in the build.

The workflow `.github/workflows/textbooks.yml` builds the books when someone starts it from the Actions page, or when
`textbooks/request.txt` changes on main (keys separated by commas, or `all`; also `nonprofit`, `fieldmanuals`,
`government`, `courses`). `python -m pytest textbooks` tests the builder with a made-up book and a made-up website.

Each book keeps its own licence; the credit and licence are on its welcome page and in `textbooks.json`.
