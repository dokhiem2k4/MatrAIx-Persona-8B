#!/usr/bin/env python3
"""Rank persona dimensions by how far flipping one moves the generated utterance.

Reads the arms built by ``ablate_persona_fields.py`` and answers one question per
dimension: does flipping it move the output further than re-running the same
prompt does?

The comparison is paired and the unit is a stimulus cell -- the same persona, the
same intent, the same subintent -- so a field is credited only when its own cell
moved, never when the pool average drifted.

    noise floor : distance(base-a, base-b)      same prompt, two samples
    effect      : distance(base-a, arm-<field>) one field flipped

A field is reported LIVE only when the bootstrap 95% CI of
``median(effect) - median(noise)`` sits entirely above zero. Anything else is
UNPROVEN: the run did not show an effect, which is not the same as showing there
is none -- a wider run may still find one.

Distance is 1 - Jaccard over token bigrams: dependency-free, insensitive to word
order, and it does not reward mere paraphrase the way exact match punishes it.
It measures surface form, not meaning; a field that changes meaning while
keeping wording will be under-credited here, so treat a LIVE verdict as solid
and an UNPROVEN one on a semantically loaded field as worth a second look with
embeddings.

    uv run python scripts/score_persona_ablation.py data/ablation
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KEY = ("persona_id", "intent_code", "subintent_code")
FIELD = "first_input"


def bigrams(text: str) -> set[str]:
    toks = [t for t in "".join(c.lower() if c.isalnum() else " " for c in text).split() if t]
    if len(toks) < 2:
        return set(toks)
    return {"{} {}".format(toks[i], toks[i + 1]) for i in range(len(toks) - 1)}


def distance(a: str, b: str) -> float:
    ga, gb = bigrams(a), bigrams(b)
    if not ga and not gb:
        return 0.0
    return 1.0 - len(ga & gb) / len(ga | gb)


def read_arm(path: Path) -> dict[tuple[str, ...], str]:
    if not path.is_file():
        return {}
    rows: dict[tuple[str, ...], str] = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            text = (row.get(FIELD) or "").strip()
            if not text:
                continue
            rows[tuple((row.get(k) or "").strip() for k in KEY)] = text
    return rows


def paired(a: dict, b: dict) -> tuple[list[float], list[tuple[str, ...]]]:
    keys = sorted(set(a) & set(b))
    return [distance(a[k], b[k]) for k in keys], keys


def bootstrap_ci(effect: list[float], noise: list[float], *, iters: int = 4000,
                 seed: int = 42) -> tuple[float, float]:
    """95% CI of median(effect) - median(noise), resampling each arm separately."""
    rng = random.Random(seed)
    deltas = []
    for _ in range(iters):
        e = statistics.median(rng.choices(effect, k=len(effect)))
        n = statistics.median(rng.choices(noise, k=len(noise)))
        deltas.append(e - n)
    deltas.sort()
    lo = deltas[int(0.025 * len(deltas))]
    hi = deltas[min(int(0.975 * len(deltas)), len(deltas) - 1)]
    return lo, hi


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dir", type=Path, help="directory holding manifest.json and <arm>.csv")
    ap.add_argument("--min-cells", type=int, default=12,
                    help="an arm with fewer paired cells is reported, never ranked")
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()

    run_dir = args.run_dir if args.run_dir.is_absolute() else REPO_ROOT / args.run_dir
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))

    base_a = read_arm(run_dir / "base-a.csv")
    base_b = read_arm(run_dir / "base-b.csv")
    if not base_a or not base_b:
        raise SystemExit(
            "cần cả base-a.csv và base-b.csv trong {} -- không có sàn nhiễu thì "
            "mọi trường đều trông như có tác dụng".format(run_dir)
        )
    noise, noise_keys = paired(base_a, base_b)
    if len(noise) < args.min_cells:
        raise SystemExit("sàn nhiễu chỉ có {} ô, quá ít để so".format(len(noise)))

    noise_med = statistics.median(noise)
    print("sàn nhiễu: {} ô ghép cặp, khoảng cách trung vị {:.3f}".format(len(noise), noise_med))
    print("  (chạy lại cùng prompt đã tự đổi {:.0f}% số bigram)".format(noise_med * 100))
    print()

    results = []
    for arm in manifest["arms"]:
        dim = arm.get("mutated_dimension")
        if not dim:
            continue
        mutated = read_arm(run_dir / "{}.csv".format(arm["tag"]))
        if not mutated:
            results.append({"dimension": dim, "verdict": "MISSING", "cells": 0})
            continue
        common = sorted(set(base_a) & set(mutated) & set(noise_keys))
        if len(common) < args.min_cells:
            results.append({"dimension": dim, "verdict": "THIN", "cells": len(common)})
            continue
        eff = [distance(base_a[k], mutated[k]) for k in common]
        nz = [distance(base_a[k], base_b[k]) for k in common]
        lo, hi = bootstrap_ci(eff, nz)
        delta = statistics.median(eff) - statistics.median(nz)
        results.append({
            "dimension": dim,
            "cells": len(common),
            "effect_median": round(statistics.median(eff), 4),
            "noise_median": round(statistics.median(nz), 4),
            "delta": round(delta, 4),
            "ci95": [round(lo, 4), round(hi, 4)],
            "verdict": "LIVE" if lo > 0 else "UNPROVEN",
        })

    rank = sorted(
        [r for r in results if r.get("verdict") in {"LIVE", "UNPROVEN"}],
        key=lambda r: (r["verdict"] != "LIVE", -r["delta"]),
    )
    print("{:<28} {:>5} {:>8} {:>8} {:>8}  {:<9} {}".format(
        "dimension", "ô", "hiệu ứng", "nhiễu", "chênh", "kết luận", "CI95"))
    for r in rank:
        print("{:<28} {:>5} {:>8.3f} {:>8.3f} {:>+8.3f}  {:<9} [{:+.3f}, {:+.3f}]".format(
            r["dimension"], r["cells"], r["effect_median"], r["noise_median"],
            r["delta"], r["verdict"], r["ci95"][0], r["ci95"][1]))

    broken = [r for r in results if r.get("verdict") in {"MISSING", "THIN"}]
    if broken:
        print()
        for r in broken:
            print("  {:<28} {} ({} ô) -- chưa chấm được".format(
                r["dimension"], r["verdict"], r["cells"]))

    live = [r for r in rank if r["verdict"] == "LIVE"]
    print()
    print("{} / {} trường có tác dụng vượt sàn nhiễu.".format(len(live), len(rank)))
    if live:
        print("Giữ: {}".format(", ".join(r["dimension"] for r in live)))

    if args.json_out:
        out = args.json_out if args.json_out.is_absolute() else REPO_ROOT / args.json_out
        out.write_text(json.dumps({
            "noise_floor_median": round(noise_med, 4),
            "noise_cells": len(noise),
            "results": results,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print("đã ghi {}".format(out.relative_to(REPO_ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
