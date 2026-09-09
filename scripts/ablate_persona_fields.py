#!/usr/bin/env python3
"""Decide which persona dimensions actually move the model, by flipping them.

A persona carries ~1,297 dimensions and roughly 700 of them reach the rendered
system prompt. Nobody knows which ones change what the driver says, and the
question cannot be answered by reading the catalog: it depends on the model.

This script runs the two free screens first and only then builds the paid
experiment, because most candidate fields die in the free screens:

  screen 1 -- variance.  A dimension holding the same value across the whole
              pool cannot distinguish two personas. Zero bits, zero effect,
              no experiment needed.

  screen 2 -- reachability.  ``collect_dimension_items`` drops a value equal to
              the schema default, so a dimension can sit in the yaml and never
              appear in the prompt. Flip it and diff the rendered profile: if
              the text is byte-identical, the effect is provably zero.

  experiment -- paired ablation.  For each surviving field, write a copy of the
              pool with that one field flipped and nothing else touched, emit a
              stage-1 recipe per pool, and let ``matraix run`` produce the
              utterances. Scoring is ``score_persona_ablation.py``.

The base pool is emitted TWICE (``base-a``, ``base-b``) on purpose. Re-running
the same prompt gives different text all by itself, so a mutation that moves the
output less than that noise floor has not been shown to do anything. Without the
two base runs every field looks alive and the experiment answers nothing.

    # screens only, no files written
    uv run python scripts/ablate_persona_fields.py --dry-run

    # screens + build the experiment
    uv run python scripts/ablate_persona_fields.py \\
        --pool vn-drivers --personas 8 --out-dir data/ablation
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from persona_tiers import persona_paths  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from matraix.persona_dimension_catalog import (  # noqa: E402
    DEFAULT_CATALOG_PATH,
    collect_dimension_items,
    load_dimension_catalog,
)

# The shortlist under test: fields with a plausible channel to the answer of an
# in-car assistant. Anything not listed here is not being claimed to be dead --
# it is being claimed to be untested. Add to the list rather than arguing.
CANDIDATES = [
    # content -- what the assistant should say or do
    "vn_assistant_task_scope",
    "vn_usual_companion",
    "lstyle_commute_mode",
    "demo_driver_status",
    "skill_driving",
    "topic_cars",
    # form -- how it says it
    "vn_address_register",
    "cog_verbosity",
    "cog_formality",
    "tone_expected",
    "register",
    "english_proficiency",
    "vn_locality",
    # threshold -- when it asks again, concedes, refuses
    "cog_patience",
    "cog_skepticism",
    "vn_retry_tolerance",
    "vn_voice_privacy_comfort",
    "trust_level",
    "safety_sensitivity",
    "att_voice_assistant",
    "att_self_driving_cars",
    "att_electric_vehicles",
    # turn-layer fields, included so the report can show what they cost -- these
    # describe a moment, not a person, and should not live in a persona at all
    "intent",
    "emotional_state",
    "time_pressure",
    "query_complexity",
    "prior_context",
    "device_context",
    "modality_pref",
]


def entropy(counter: collections.Counter) -> float:
    total = sum(counter.values())
    if total <= 0:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counter.values() if c)


def load_pool(pool_dir: Path) -> list[tuple[str, dict[str, Any]]]:
    out = []
    for path in persona_paths(pool_dir):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("dimensions"), dict):
            out.append((path.name, data))
    if not out:
        raise SystemExit("no persona_*.yaml under {}".format(pool_dir))
    return out


def flip_value(dim_id: str, current: Any, catalog: dict[str, Any], pool_values: list[Any]) -> Any:
    """Pick the counterfactual: the value furthest along the declared scale.

    Scales in this schema are ordered (``Very uncomfortable`` .. ``Very
    comfortable``), so distance along the list is the strongest legal contrast.
    Mirroring the index is not enough: a value sitting on the midpoint of an
    odd-length scale mirrors onto itself, which silently killed ``cog_verbosity``
    (``Balanced``), ``cog_skepticism`` (``Moderate``) and ``vn_retry_tolerance``
    (``Annoyed``) -- three of the fields the experiment exists to test. Taking
    the argmax of the index distance keeps a midpoint value testable. Falling
    back to the pool's own values keeps the flip inside the observed support
    when the catalog carries no value list.
    """
    meta = catalog["by_id"].get(dim_id) or {}
    values = [v for v in (meta.get("values") or []) if v is not None]
    if not values:
        values = sorted({v for v in pool_values if v is not None}, key=str)
    values = [v for v in values if str(v) != str(current)]
    if not values:
        return None
    if current in (meta.get("values") or []):
        idx = (meta.get("values") or []).index(current)
        ordered = meta.get("values") or []
        return max(values, key=lambda v: abs(ordered.index(v) - idx))
    return values[-1]


def rendered_profile(dimensions: dict[str, Any]) -> str:
    grouped = collect_dimension_items(dimensions)
    parts = []
    for heading, items in grouped.items():
        for dim_id, label, text in items:
            parts.append("{}|{}|{}|{}".format(heading, dim_id, label, text))
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pool", default="vn-drivers")
    ap.add_argument("--personas", type=int, default=8, help="how many personas carry the experiment")
    ap.add_argument("--out-dir", type=Path, default=Path("data/ablation"))
    ap.add_argument("--job-prefix", default="abl")
    ap.add_argument("--intent", action="append", default=[], dest="intents",
                    help="restrict stage 1 to these utterance intents (repeatable)")
    ap.add_argument("--dry-run", action="store_true", help="print the two screens, write nothing")
    args = ap.parse_args()

    pool_dir = REPO_ROOT / "persona" / "datasets" / args.pool
    personas = load_pool(pool_dir)
    catalog = load_dimension_catalog(DEFAULT_CATALOG_PATH)

    values_by_dim: dict[str, list[Any]] = collections.defaultdict(list)
    for _, data in personas:
        for k, v in data["dimensions"].items():
            values_by_dim[k].append(v)

    probe = personas[0][1]["dimensions"]
    base_profile = rendered_profile(probe)

    rows = []
    for dim in CANDIDATES:
        if dim not in values_by_dim:
            rows.append((dim, 0.0, None, "ABSENT", "không có trong pool"))
            continue
        counts = collections.Counter(str(v) for v in values_by_dim[dim])
        bits = entropy(counts)
        flipped = flip_value(dim, probe.get(dim), catalog, values_by_dim[dim])

        if bits <= 1e-9:
            rows.append((dim, bits, flipped, "DEAD", "hằng số trên cả pool"))
            continue
        if flipped is None:
            rows.append((dim, bits, flipped, "DEAD", "không có giá trị đối chứng"))
            continue
        mutated = dict(probe)
        mutated[dim] = flipped
        if rendered_profile(mutated) == base_profile:
            rows.append((dim, bits, flipped, "DEAD", "lật xong prompt không đổi"))
            continue
        rows.append((dim, bits, flipped, "TEST", "{!r} -> {!r}".format(probe.get(dim), flipped)))

    live = [r for r in rows if r[3] == "TEST"]
    print("screen 1+2 -- {} ứng viên, {} qua được, {} loại miễn phí".format(
        len(rows), len(live), len(rows) - len(live)))
    print()
    print("{:<28} {:>6}  {:<6} {}".format("dimension", "bits", "kết", "đối chứng"))
    for dim, bits, _flipped, verdict, note in sorted(rows, key=lambda r: (r[3] != "TEST", -r[1])):
        print("{:<28} {:>6.2f}  {:<6} {}".format(dim, bits, verdict, note))

    if args.dry_run:
        print("\n--dry-run: không ghi gì. Bỏ cờ này để dựng thí nghiệm cho {} trường.".format(len(live)))
        return 0

    if args.out_dir.is_absolute():
        raise SystemExit("--out-dir phải là đường dẫn tương đối trong repo")
    out = REPO_ROOT / args.out_dir
    # generate_vita_stage1_jobs.py resolves a pool as persona/datasets/<pool>/**,
    # so the mutated pools have to live there -- anywhere else and --persona-pool
    # silently finds nothing and every arm runs the unmutated persona.
    pools_root = REPO_ROOT / "persona" / "datasets" / "{}-abl".format(args.pool)
    if pools_root.exists():
        shutil.rmtree(pools_root)

    def write_pool(tag: str, mutate_dim: str | None) -> Path:
        dst = pools_root / tag
        dst.mkdir(parents=True, exist_ok=True)
        for name, data in personas[: args.personas]:
            copy = json.loads(json.dumps(data))
            if mutate_dim:
                flipped = flip_value(
                    mutate_dim, copy["dimensions"].get(mutate_dim), catalog, values_by_dim[mutate_dim]
                )
                if flipped is None:
                    continue
                copy["dimensions"][mutate_dim] = flipped
            copy["persona_id"] = data["persona_id"]
            (dst / name).write_text(
                yaml.safe_dump(copy, sort_keys=False, allow_unicode=True), encoding="utf-8"
            )
        return dst

    arms = [("base-a", None), ("base-b", None)] + [(dim, dim) for dim, *_ in live]
    manifest = {
        "pool": args.pool,
        "personas": [personas[i][1]["persona_id"] for i in range(min(args.personas, len(personas)))],
        "intents": args.intents,
        "noise_floor_arms": ["base-a", "base-b"],
        "arms": [],
        "screened_out": [
            {"dimension": d, "bits": round(b, 3), "reason": n}
            for d, b, _f, v, n in rows if v != "TEST"
        ],
    }
    for tag, mutate in arms:
        write_pool(tag, mutate)
        manifest["arms"].append({"tag": tag, "mutated_dimension": mutate})

    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    skips = []
    if args.intents:
        all_intents = sorted(
            p.name.replace("survey_vita-utterance-", "")
            for p in (REPO_ROOT / "application" / "tasks").glob("survey_vita-utterance-*")
        )
        skips = [i for i in all_intents if i not in args.intents]

    lines = ["#!/usr/bin/env bash", "set -eu", 'cd "$(dirname "$0")/../.."', ""]
    for tag, _ in arms:
        pool_arg = "{}-abl/{}".format(args.pool, tag)
        lines += [
            "echo '### arm {}'".format(tag),
            "uv run python scripts/generate_vita_stage1_jobs.py \\",
            "  " + " ".join("--persona={}".format(p) for p in manifest["personas"]) + " \\",
            "  --persona-pool {} \\".format(pool_arg),
            "  --out-dir configs/jobs/{}-{} \\".format(args.job_prefix, tag),
            # The continuation backslash has to live on --job-prefix whenever a
            # skip list follows it. Without it the command ended there and the
            # skip line ran as its own (failing) command, so every arm quietly
            # generated all sixteen intents instead of the two asked for -- an
            # eightfold cost increase that the script still reported as success.
            "  --job-prefix {}-{}{}".format(
                args.job_prefix, tag, " \\" if skips else ""),
            *(["  " + " ".join("--skip-intent={}".format(s) for s in skips)] if skips else []),
            "for cfg in configs/jobs/{}-{}/*.yaml; do".format(args.job_prefix, tag),
            '  intent=$(basename "$cfg" .yaml | sed "s/^{}-{}-//")'.format(args.job_prefix, tag),
            '  export MATRIX_SURVEY_TASK_PATH="application/tasks/survey_vita-utterance-${intent}"',
            '  uv run matraix run -c "$cfg" 2>&1 | tail -2',
            "done",
            "uv run python scripts/merge_vita_datasets.py jobs/{}-{}-* -o {}/{}.csv".format(
                args.job_prefix, tag, args.out_dir, tag),
            "",
        ]
    runner = out / "run_arms.sh"
    runner.write_text("\n".join(lines), encoding="utf-8")
    runner.chmod(0o755)

    print()
    print("đã dựng {} nhánh ({} đối chứng nhiễu + {} trường) cho {} persona".format(
        len(arms), 2, len(live), len(manifest["personas"])))
    print("  pools    : {} ({} nhánh)".format(pools_root.relative_to(REPO_ROOT), len(arms)))
    print("  manifest : {}".format((out / "manifest.json").relative_to(REPO_ROOT)))
    print("  chạy     : ./{}".format(runner.relative_to(REPO_ROOT)))
    print("  chấm     : uv run python scripts/score_persona_ablation.py {}".format(
        args.out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
