#!/usr/bin/env python3
"""Ask whether the instructed behaviour appeared, not whether the text moved.

``score_persona_ablation.py`` measures 1 - Jaccard over token bigrams, and the
noise floor swamped it: re-running the identical prompt already changed 41% of
bigrams, so a field had to beat that to register, and none of twenty-one did.
The metric is not wrong -- it is answering a question whose answer is dominated
by sampling variance.

A probe asks a narrower question with almost no variance in it. cog_verbosity
does not say "be different", it says how many words; vn_address_register names
the two pronouns that must appear. Counting words and matching pronouns is a
near-deterministic measurement, so an effect of the size these fields actually
have is visible in ninety cells instead of being buried by them.

Each probe returns a number per utterance. A field is credited when the arm's
distribution of that number separates from base-a's, tested with the same
paired bootstrap and the same cell key as the distance scorer, so the two
readings sit side by side rather than replacing one another.

    uv run python scripts/score_persona_probes.py data/ablation

Probes measure the surface a directive names. A field whose directive changes
meaning rather than form -- what a driver is willing to delegate, say -- has no
probe here and is reported as NO PROBE rather than as no effect.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import sys
import unicodedata
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

KEY = ("persona_id", "intent_code", "subintent_code", "seed_input")
FIELD = "first_input"
BOOTSTRAP = 2000
SEED = 20260910


def _fold(text: str) -> str:
    """Lowercase and strip diacritics, so a probe matches how people type."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return stripped.replace("đ", "d")


def _words(text: str) -> list[str]:
    return [w for w in _fold(text).replace(",", " ").replace(".", " ").split() if w]


def probe_word_count(text: str) -> float:
    """cog_verbosity: the directive names a word budget."""
    return float(len(_words(text)))


#: vn_address_register: the pair of pronouns the directive requires. Folded,
#: because "chị" is typed both with and without its diacritic.
ADDRESS_MARKERS = {
    "anh/em": ("anh", "em"),
    "chi/em": ("chi", "em"),
    "em/anh-chi": ("em", "anh", "chi"),
    "co-chu/con": ("co", "chu", "con"),
    "bac/chau": ("bac", "chau"),
    "toi/ban": ("toi", "ban"),
    "minh/ban": ("minh", "ban"),
}


def probe_address_pair(value: str) -> Callable[[str], float]:
    markers = ADDRESS_MARKERS.get(value, ())

    def probe(text: str) -> float:
        words = set(_words(text))
        return float(sum(1 for m in markers if m in words))

    return probe


#: cog_formality: deference particles against clipped/slang forms. A directive
#: that says "ends with ạ" is measurable; "sounds casual" would not be.
POLITE_MARKERS = ("a", "nhe", "vui long", "lam on", "giup", "cam on", "da")
SLANG_MARKERS = ("ok", "oke", "thoi", "luon", "di", "nhanh len", "ne", "hen")


def probe_politeness(text: str) -> float:
    words = _words(text)
    polite = sum(1 for m in POLITE_MARKERS if m in words)
    slang = sum(1 for m in SLANG_MARKERS if m in words)
    return float(polite - slang)


#: accent_region: regional lexicon that a Northern and a Southern speaker do
#: not share. Positive is Southern, negative Northern; a Mixed speaker sits
#: near zero. Only pairs with no overlap in meaning are listed.
NORTHERN = ("re", "bo me", "bao", "o to", "vao", "the nao")
SOUTHERN = ("queo", "ba ma", "noi", "xe hoi", "vo", "sao")


def probe_accent(text: str) -> float:
    folded = _fold(text)
    north = sum(1 for m in NORTHERN if m in folded)
    south = sum(1 for m in SOUTHERN if m in folded)
    return float(south - north)


#: field -> probe over an utterance. These do not depend on which value the
#: persona holds: more words is more words.
PROBES: dict[str, Callable[[str], float]] = {
    "cog_verbosity": probe_word_count,
    "cog_formality": probe_politeness,
    "tone_expected": probe_word_count,
    "accent_region": probe_accent,
}

#: field -> builds a probe from the value that persona holds. vn_address_register
#: has no single quantity to count: the question is whether the two pronouns
#: this persona was told to use are the ones that appeared.
VALUE_PROBES: dict[str, Callable[[str], Callable[[str], float]]] = {
    "vn_address_register": probe_address_pair,
}


def arm_values(
    pool: Path, arm: str, field: str, persona_ids: set[str]
) -> dict[str, str]:
    """The value each persona holds for ``field`` inside arm directory ``arm``.

    The arm directory is named after the field it mutates for every arm except
    the two baselines, so the two must be passed separately -- reading
    ``dimensions["base-a"]`` returns nothing and silently drops the probe.
    """
    import yaml

    out: dict[str, str] = {}
    for pid in persona_ids:
        path = pool / arm / f"persona_{pid}.yaml"
        if not path.is_file():
            continue
        dims = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get(
            "dimensions"
        ) or {}
        value = dims.get(field)
        if value is not None:
            out[pid] = str(value)
    return out


def paired_shift_by_persona(
    base: dict[tuple[str, ...], str],
    arm: dict[tuple[str, ...], str],
    probes: dict[str, Callable[[str], float]],
) -> list[float]:
    """Per-cell shift where each persona is scored against its own target."""
    shifts = []
    for key, base_text in base.items():
        if key not in arm:
            continue
        probe = probes.get(key[0])
        if probe is None:
            continue
        shifts.append(probe(arm[key]) - probe(base_text))
    return shifts


def load_arm(directory: Path, name: str) -> dict[tuple[str, ...], str]:
    path = directory / f"{name}.csv"
    rows: dict[tuple[str, ...], str] = {}
    with path.open(encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            rows[tuple(row[k] for k in KEY)] = row[FIELD]
    return rows


def paired_shift(
    base: dict[tuple[str, ...], str],
    arm: dict[tuple[str, ...], str],
    probe: Callable[[str], float],
) -> list[float]:
    """Per-cell change in the probed quantity: same persona, same stimulus."""
    return [
        probe(arm[key]) - probe(base[key])
        for key in base
        if key in arm
    ]


def bootstrap_ci(
    values: list[float], rng: random.Random, *, reps: int = BOOTSTRAP
) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    medians = []
    n = len(values)
    for _ in range(reps):
        medians.append(statistics.median(rng.choices(values, k=n)))
    medians.sort()
    return (medians[int(0.025 * reps)], medians[int(0.975 * reps)])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("directory", type=Path)
    ap.add_argument("--json-out", type=Path)
    ap.add_argument(
        "--pool",
        type=Path,
        default=REPO_ROOT / "persona/datasets/vn-drivers-abl",
        help="ablation persona pool, for probes that need each arm's value",
    )
    args = ap.parse_args()

    base = load_arm(args.directory, "base-a")
    noise_arm = load_arm(args.directory, "base-b")
    rng = random.Random(SEED)

    results = []
    compliance: list[dict] = []
    for field in sorted(PROBES):
        path = args.directory / f"{field}.csv"
        if not path.is_file():
            continue
        arm = load_arm(args.directory, field)

        probe = PROBES[field]
        effect = paired_shift(base, arm, probe)
        noise = paired_shift(base, noise_arm, probe)
        e_med = statistics.median(effect) if effect else 0.0
        n_med = statistics.median(noise) if noise else 0.0
        lo, hi = bootstrap_ci([e - n_med for e in effect], rng)
        live = lo > 0 or hi < 0
        results.append(
            {
                "field": field,
                "cells": len(effect),
                "effect_median": e_med,
                "noise_median": n_med,
                "delta": e_med - n_med,
                "ci95": [lo, hi],
                "verdict": "LIVE" if live else "UNPROVEN",
            }
        )

    # Compliance, not displacement. The first version of this probe counted the
    # arm's target pronouns in both arms and scored zero -- which read as "no
    # effect" when the truth was the opposite: base-a said "chi" in 27 of 30
    # utterances and the arm dropped it entirely, landing on "toi" rather than
    # the "minh/ban" it was told to use. The field moved the output; the model
    # just did not obey the value. Those are different findings and a paired
    # difference cannot tell them apart, so each arm is scored against its own
    # instruction and the two rates are reported side by side.
    persona_ids = {key[0] for key in base}
    for field in sorted(VALUE_PROBES):
        if not (args.directory / f"{field}.csv").is_file() or not args.pool:
            continue
        arm = load_arm(args.directory, field)
        targets = {
            "base": arm_values(args.pool, "base-a", field, persona_ids),
            "arm": arm_values(args.pool, field, field, persona_ids),
        }
        if not targets["base"] or not targets["arm"]:
            continue

        def rate(rows, target_values):
            hits = [
                1.0 if VALUE_PROBES[field](target_values[key[0]])(text) > 0 else 0.0
                for key, text in rows.items()
                if key[0] in target_values
            ]
            return statistics.mean(hits) if hits else 0.0

        base_rate = rate(base, targets["base"])
        arm_rate = rate(arm, targets["arm"])
        compliance.append(
            {
                "field": field,
                "cells": len(base),
                "base_followed_its_own_value": base_rate,
                "arm_followed_its_own_value": arm_rate,
                "base_value_survived_in_arm": rate(arm, targets["base"]),
            }
        )

    results.sort(key=lambda r: -abs(r["delta"]))
    print("probe                   cells   effect    noise    delta  verdict   CI95")
    for r in results:
        print(
            "{field:22s} {cells:5d} {effect_median:8.2f} {noise_median:8.2f} "
            "{delta:+8.2f}  {verdict:8s} [{lo:+.2f}, {hi:+.2f}]".format(
                lo=r["ci95"][0], hi=r["ci95"][1], **r
            )
        )
    for c in compliance:
        print(
            "\ncompliance -- {field}: the persona used the pronouns it was told to\n"
            "  base-a arm: {base_followed_its_own_value:.0%} of utterances\n"
            "  mutated arm: {arm_followed_its_own_value:.0%} of utterances\n"
            "  base-a's pronouns still present in the mutated arm: "
            "{base_value_survived_in_arm:.0%}".format(**c)
        )
        if c["arm_followed_its_own_value"] < 0.5 <= c["base_followed_its_own_value"]:
            print(
                "  -> the field changed the output but the instructed value was "
                "not followed; that is a prompt problem, not a dead field."
            )

    live = sum(1 for r in results if r["verdict"] == "LIVE")
    print(f"\n{live} / {len(results)} probed fields moved their own measure.")

    unprobed = sorted(
        p.stem
        for p in args.directory.glob("*.csv")
        if p.stem not in PROBES
        and p.stem not in VALUE_PROBES
        and not p.stem.startswith("base-")
    )
    print(f"NO PROBE ({len(unprobed)}): {', '.join(unprobed)}")
    print("  A field with no probe is unmeasured here, not ineffective.")

    if args.json_out:
        args.json_out.write_text(
            json.dumps(
                {"probes": results, "compliance": compliance, "unprobed": unprobed},
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
