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

## Licence

The models are under the **Apache License 2.0**, the licence of Qwen3 and Qwen3-VL (Alibaba Cloud) and of
huihui-ai's versions. The full text is in [LICENSE](LICENSE). See [NOTICE](NOTICE) for what was changed. The
conversion script `convert_models.py` is also under the Apache License 2.0.

## How the models are made

The workflow `.github/workflows/convert.yml` converts each model and uploads it:

1. download the original model at its pinned commit;
2. convert it with `onnxruntime_genai.models.builder` or `optimum-cli export openvino`, with 4-bit weights;
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
