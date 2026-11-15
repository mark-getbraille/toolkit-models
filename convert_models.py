"""Convert the planned engine models (app/toolkit/vision/engines/models.py, the ones marked published_by_workflow) and
publish them to the release "engine-models" of the public repository mark-getbraille/toolkit-models, where the
program downloads them (models.RELEASE). The toolkit's own repository is private, so the conversion runs there: this
script and a plan of the models (plan.json, written by --export from models.py) are copied into that repository, whose
workflow (.github/workflows/convert.yml) runs them with --plan plan.json. It can also run on a developer's computer.

To change what is converted: change models.py here, then
    python tools/convert_models.py --export ../toolkit-models       (writes plan.json and copies this script)
and commit and push the toolkit-models repository.

For each model key:
  1. download the original model (safetensors) at its pinned commit: hf download <repo> --revision <commit>;
  2. ONNX Runtime GenAI models: python -m onnxruntime_genai.models.builder -m <repo> -i <download> -o <out> -p int4
     -e dml (the "gpu" variant, for DirectML) and -e cpu (the "cpu" variant);
     OpenVINO models: optimum-cli export openvino --model <download> --task <task> --weight-format int4 <out> (the
     "any" variant, for Intel graphics and processors) and, for text models, the same with --sym --ratio 1.0
     --group-size -1 (the "npu" variant: NPUs need symmetric, channel-wise 4-bit weights);
  3. zip each output folder as <key>-<variant>.zip and record its size and SHA-256 in manifest-<key>.json; a zip over
     GitHub's 2 GB limit for one release file is cut into parts of models.PART_BYTES (<zip>.001, .002 ...; split_file),
     and the manifest records how many ("parts"); the program downloads the parts and joins them;
  4. with --upload: gh release upload engine-models <zip or parts> --clobber as soon as each zip is made (tried again
     on a network error), then the zip is deleted to free the disk; the manifest last. The release is created first
     when it does not exist.
After publishing, copy the printed sizes and SHA-256 into the model's Variant entries in models.py: only then does the
toolkit offer the model (EngineModel.ready).

What it needs (see the workflow for the exact packages): about 2.5 times the model's original size in free disk space
for each conversion (a Qwen3 8B: 16 GB download, 5 GB output, 5 GB zip: about 30 GB), and memory for the full model in
16-bit form (8B: about 17 GB; a swap file helps). A 4B model takes about 20 minutes, an 8B model about 45 on a
4-core runner.

    python tools/convert_models.py --dry-run ort-qwen3-4b-abliterated      (print the commands only)
    python tools/convert_models.py --upload ov-qwen3vl-4b-abliterated
    python tools/convert_models.py --list-json all                          (the keys, for the workflow's matrix)"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "app"))

try:
    from toolkit.vision.engines import models   # noqa: E402 - after the path is set
except ImportError:                             # in the toolkit-models repository: only plan.json (--plan)
    models = None

PART_BYTES = models.PART_BYTES if models else 1_900_000_000      # the same value as models.PART_BYTES
# The models to convert: key -> a model (models.EngineModel, or the same fields read from plan.json by load_plan).
MODELS = dict(models.MODELS) if models else {}

RELEASE_TAG = "engine-models"
UPLOAD_TRIES = 4
UPLOAD_PAUSE = 30            # seconds before trying an upload again


def planned_keys():
    """The keys of the models the workflow converts (published_by_workflow), in table order."""
    return [k for k, m in MODELS.items() if getattr(m, "published_by_workflow", True)]


def download_command(model, source_dir):
    """The command that downloads the original model at its pinned commit into source_dir."""
    return ["hf", "download", model.base_model, "--revision", model.base_revision, "--local-dir", source_dir]


def convert_commands(model, source_dir, out_dir, python=sys.executable):
    """[(variant name, output folder, command)] that convert model (a models.EngineModel) from source_dir into
    out_dir/<key>-<variant>."""
    commands = []
    for variant in model.variants.values():
        target = os.path.join(out_dir, f"{model.key}-{variant.name}")
        if model.engine == "ort-genai":
            provider = "dml" if "directml" in variant.devices else "cpu"
            command = [python, "-m", "onnxruntime_genai.models.builder", "-m", model.base_model, "-i", source_dir,
                       "-o", target, "-p", "int4", "-e", provider,
                       "-c", os.path.join(out_dir, "cache")]
        elif model.engine == "openvino":
            task = "image-text-to-text" if model.vision else "text-generation-with-past"
            command = ["optimum-cli", "export", "openvino", "--model", source_dir, "--task", task,
                       "--weight-format", "int4"]
            if variant.name == "npu":
                command += ["--sym", "--ratio", "1.0", "--group-size", "-1"]
            command.append(target)
        else:
            raise ValueError(f"unknown engine {model.engine}")
        commands.append((variant.name, target, command))
    return commands


def sha256_of(path):
    """The SHA-256 of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def zip_folder(folder, archive):
    """Zip folder's files (names relative to it; 64-bit zip for files over 4 GB; stored: the weights do not
    compress)."""
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
        for base, _dirs, files in os.walk(folder):
            for name in sorted(files):
                path = os.path.join(base, name)
                z.write(path, os.path.relpath(path, folder).replace(os.sep, "/"))


def split_file(path, part_bytes=None):
    """Cut a file bigger than part_bytes (PART_BYTES) into numbered parts <path>.001, <path>.002 ... and
    delete it; returns the part paths ([path] itself when it is small enough). The parts are cut off the end of the
    file one by one (the file shortened each time), so it needs only one part's worth of extra disk space."""
    part_bytes = part_bytes or PART_BYTES
    size = os.path.getsize(path)
    if size <= part_bytes:
        return [path]
    count = -(-size // part_bytes)
    parts = [f"{path}.{i:03d}" for i in range(1, count + 1)]
    with open(path, "r+b") as f:
        for number in range(count, 1, -1):
            start = (number - 1) * part_bytes
            f.seek(start)
            with open(parts[number - 1], "wb") as out:
                shutil.copyfileobj(f, out, 1 << 20)
            f.truncate(start)
    os.replace(path, parts[0])
    return parts


def run(command, dry_run):
    """Print a command and run it (not with dry_run); raises CalledProcessError when it fails."""
    print("+ " + " ".join(command), flush=True)
    if not dry_run:
        subprocess.run(command, check=True)


def upload(paths, dry_run, tries=UPLOAD_TRIES, pause=UPLOAD_PAUSE, runner=subprocess.run, sleep=time.sleep):
    """Upload files to the release (gh release upload --clobber), creating the release when it is missing; each
    upload is tried again up to tries times."""
    view = ["gh", "release", "view", RELEASE_TAG]
    create = ["gh", "release", "create", RELEASE_TAG, "--title", "Engine models",
              "--notes", "Converted models of the ONNX Runtime GenAI and OpenVINO engines (tools/convert_models.py)."]
    print("+ " + " ".join(view), flush=True)
    if not dry_run and runner(view, capture_output=True).returncode != 0:
        print("+ " + " ".join(create), flush=True)
        if runner(create).returncode != 0:
            raise RuntimeError(f"the release {RELEASE_TAG} could not be created")
    for path in paths:
        command = ["gh", "release", "upload", RELEASE_TAG, path, "--clobber"]
        for attempt in range(1, tries + 1):
            print("+ " + " ".join(command), flush=True)
            if dry_run or runner(command).returncode == 0:
                break
            if attempt == tries:
                raise RuntimeError(f"upload of {path} failed {tries} times")
            sleep(pause)


def convert(key, out_dir, dry_run=False, keep_source=False, publish=None):
    """Convert one model and zip it; with publish (a function given the file paths, upload), each variant's zip is
    published as soon as it is made and then deleted, so the disk holds only one at a time. Returns its manifest
    {"key", "base_model", "base_revision", "variants": {name:
    {"asset", "size", "sha256", "files", "parts"}}} (sizes 0 with dry_run; files: the names to upload, the zip or its
    parts)."""
    model = MODELS[key]
    source = os.path.join(out_dir, "source", key)
    run(download_command(model, source), dry_run)
    manifest = {"key": key, "engine": model.engine, "base_model": model.base_model,
                "base_revision": model.base_revision, "variants": {}}
    for name, target, command in convert_commands(model, source, out_dir):
        run(command, dry_run)
        shutil.rmtree(os.path.join(out_dir, "cache"), ignore_errors=True)   # the ONNX builder's work files
        archive = os.path.join(out_dir, f"{model.key}-{name}.zip")
        entry = {"asset": os.path.basename(archive), "size": 0, "sha256": "", "files": [os.path.basename(archive)],
                 "parts": 1}
        if not dry_run:
            zip_folder(target, archive)
            shutil.rmtree(target, ignore_errors=True)      # the zip is kept; the folder's disk space is needed
            entry.update(size=os.path.getsize(archive), sha256=sha256_of(archive))
            pieces = split_file(archive)
            entry.update(files=[os.path.basename(p) for p in pieces], parts=len(pieces))
        if publish is not None:
            publish([os.path.join(out_dir, f) for f in entry["files"]])
            for f in entry["files"]:
                if not dry_run:
                    os.remove(os.path.join(out_dir, f))
        manifest["variants"][name] = entry
    if not keep_source and not dry_run:
        shutil.rmtree(source, ignore_errors=True)
    path = os.path.join(out_dir, f"manifest-{key}.json")
    if not dry_run:
        os.makedirs(out_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1)
    return manifest


def merge_manifests(paths, target):
    """Merge manifest-<key>.json files into one manifest.json {key: manifest}, keeping the entries already there."""
    merged = {}
    if os.path.exists(target):
        with open(target, encoding="utf-8") as f:
            merged = json.load(f)
    for path in paths:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        merged[data["key"]] = data
    with open(target, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=1, sort_keys=True)
    return merged


def table_lines(manifest):
    """The Variant(...) values to paste into models.py for a published model."""
    lines = []
    for name, entry in manifest["variants"].items():
        parts = entry.get("parts", 1)
        lines.append(f'    {manifest["key"]} {name}: size={entry["size"]}, sha256="{entry["sha256"]}"'
                     + (f", parts={parts}" if parts > 1 else ""))
    return lines


PLAN_FIELDS = ("key", "engine", "base_model", "base_revision", "vision")


def plan_of(keys=None):
    """The plan of the models to convert (for plan.json): [{key, engine, base_model, base_revision, vision,
    variants: [{name, devices}]}], in table order."""
    return [dict({f: getattr(MODELS[k], f) for f in PLAN_FIELDS},
                 variants=[{"name": v.name, "devices": list(v.devices)} for v in MODELS[k].variants.values()])
            for k in (keys or planned_keys())]


def load_plan(path):
    """Read plan.json into MODELS (each model with the fields of PLAN_FIELDS and variants {name: variant with name
    and devices}), replacing what was there."""
    from types import SimpleNamespace
    with open(path, encoding="utf-8") as f:
        plan = json.load(f)
    MODELS.clear()
    for entry in plan:
        variants = {v["name"]: SimpleNamespace(name=v["name"], devices=tuple(v["devices"])) for v in entry["variants"]}
        MODELS[entry["key"]] = SimpleNamespace(**{f: entry[f] for f in PLAN_FIELDS}, variants=variants,
                                               published_by_workflow=True)


def export(folder):
    """Write plan.json (the planned models) and a copy of this script into folder (the toolkit-models checkout)."""
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "plan.json"), "w", encoding="utf-8") as f:
        json.dump(plan_of(), f, indent=1)
        f.write("\n")
    shutil.copyfile(os.path.abspath(__file__), os.path.join(folder, "convert_models.py"))


def resolve_keys(words):
    """The model keys of the words given ("all", or keys separated by spaces or commas); raises SystemExit for an
    unknown key or one that is not a planned conversion."""
    keys = []
    for word in words:
        keys += [w.strip() for w in word.split(",") if w.strip()]
    if not keys or keys == ["all"]:
        return planned_keys()
    unknown = [k for k in keys if k not in planned_keys()]
    if unknown:
        raise SystemExit(f"not a planned conversion: {', '.join(unknown)} (choose from {', '.join(planned_keys())})")
    return keys


def main(argv=None):
    """The command line (see the module docstring)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("keys", nargs="*", help="model keys, or all")
    parser.add_argument("--out", default=os.path.join(ROOT, "build", "engine-models"), help="working folder")
    parser.add_argument("--dry-run", action="store_true", help="print the commands only")
    parser.add_argument("--upload", action="store_true", help="upload the zips and manifest to the release")
    parser.add_argument("--keep-source", action="store_true", help="keep the downloaded original model")
    parser.add_argument("--list-json", action="store_true", help="print the keys as JSON and stop")
    parser.add_argument("--merge", nargs="*", metavar="MANIFEST", help="merge manifest files into --out/manifest.json")
    parser.add_argument("--plan", metavar="FILE", help="read the models from this plan.json instead of models.py")
    parser.add_argument("--export", metavar="FOLDER", help="write plan.json and a copy of this script into FOLDER")
    args = parser.parse_args(argv)
    if args.plan:
        load_plan(args.plan)
    if args.export:
        export(args.export)
        return 0
    if args.merge is not None:
        target = os.path.join(args.out, "manifest.json")
        merge_manifests(args.merge, target)
        if args.upload:
            upload([target], args.dry_run)
        return 0
    keys = resolve_keys(args.keys)
    if args.list_json:
        print(json.dumps(keys))
        return 0
    if not args.dry_run:
        os.makedirs(args.out, exist_ok=True)
    for key in keys:
        publish = (lambda paths: upload(paths, args.dry_run)) if args.upload else None
        manifest = convert(key, args.out, args.dry_run, args.keep_source, publish)
        if args.upload:
            upload([os.path.join(args.out, f"manifest-{key}.json")], args.dry_run)
        print("\n".join(table_lines(manifest)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
