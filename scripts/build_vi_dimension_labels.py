#!/usr/bin/env python3
"""Translate persona dimension labels and enum values into a label-pack source.

The UI locale pack translates chrome -- buttons, headings, column titles. It
does not touch the persona attributes themselves, so a Vietnamese UI still
shows "Southeast Asia", "Skilled Trades", "Get task done" on every card. Those
come from ``dimensions.json`` and need a label pack, which is a display-only
overlay: canonical ids and values stay English everywhere data is stored,
filtered, stratified or scored.

Translating each dimension separately would mean ~6,300 strings, but the enum
values repeat heavily -- hundreds of ``fam_*`` dimensions share
Expert/Proficient/Familiar/Aware/None. Translating the ~2,500 unique strings
once and expanding cuts the work by more than half and, more importantly,
guarantees the same English value reads the same way everywhere.

Per-dimension independence is preserved on expansion: the pack format keeps one
entry per dimension, so a later reviewer can correct "None" on a language field
without touching "None" on a skill field.

Usage:
    uv run python scripts/build_vi_dimension_labels.py
    uv run python scripts/build_vi_dimension_labels.py --limit 200   # smoke test
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "packages/playground/src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "packages/playground/src"))

SCHEMA = REPO_ROOT / "persona/schema/dimensions.json"
SOURCES = REPO_ROOT / "persona/schema/labels/sources"

SYSTEM = """You translate persona-attribute labels into Vietnamese for a UI.

These are short noun phrases and scale points shown in table cells and chips.

Rules:
1. Keep them SHORT. Longer than the English breaks the layout.
2. Scale points must stay ordered and distinguishable. Expert/Proficient/
   Familiar/Aware/None are five ranks -- translate them as five distinct
   Vietnamese ranks, not three synonyms.
3. Keep proper nouns and place names in their standard Vietnamese form
   (Southeast Asia -> Đông Nam Á, Ha Noi -> Hà Nội).
4. Keep widely-used English technical terms as-is when Vietnamese speakers use
   them in that field: persona, marketing, blockchain, DevOps.
5. Numeric ranges and ages stay as digits (25-34 -> 25-34).

Return ONLY a JSON object mapping each input string to its Vietnamese
translation. No prose, no extra keys."""

#: Layer-1 / Layer-2 accordion titles. Small and load-bearing for the profile
#: drawer, so they are written by hand rather than machine-translated.
TAXONOMY_VI = {
    "background": "Nền tảng",
    "demographics": "Nhân khẩu",
    "language": "Ngôn ngữ",
    "education": "Học vấn",
    "career": "Nghề nghiệp",
    "psychology": "Tâm lý",
    "personality": "Tính cách",
    "worldview": "Thế giới quan",
    "decision_making": "Ra quyết định",
    "capability": "Năng lực",
    "domains": "Lĩnh vực",
    "skills": "Kỹ năng",
    "behavior": "Hành vi & tương tác",
    "personal_behavior": "Hành vi cá nhân",
    "interaction_state": "Trạng thái tương tác",
    "work_practices": "Cách làm việc",
    "technology_use": "Sử dụng công nghệ",
    "lifestyle": "Lối sống & sức khoẻ",
    "interests": "Sở thích",
    "culture": "Văn hoá & đời sống",
    "health": "Sức khoẻ",
    "other": "Khác",
    "uncategorized": "Chưa phân loại",
}


def translate(client, model: str, strings: list[str], batch_size: int) -> dict[str, str]:
    out: dict[str, str] = {}
    for start in range(0, len(strings), batch_size):
        chunk = strings[start : start + batch_size]
        try:
            response = client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": json.dumps(chunk, ensure_ascii=False)},
                ],
            )
            payload = json.loads((response.choices[0].message.content or "{}").strip())
        except Exception as exc:  # noqa: BLE001 - one bad batch must not end the run
            print("  batch {} failed: {}".format(start, str(exc)[:80]), flush=True)
            continue
        if isinstance(payload, dict):
            for key in chunk:
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    out[key] = value.strip()
        print("  {}/{}".format(len(out), len(strings)), flush=True)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", default="vi")
    parser.add_argument("--batch-size", type=int, default=60)
    parser.add_argument("--limit", type=int, help="translate only the first N strings")
    parser.add_argument(
        "--model",
        default=os.environ.get(
            "MATRIX_PERSONA_MODEL", "openrouter/google/gemini-3.5-flash-lite"
        ),
    )
    args = parser.parse_args()

    from openai import OpenAI
    from playground.model_client import openrouter_openai_client_kwargs

    kwargs = openrouter_openai_client_kwargs(args.model)
    client = OpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"])

    dims = json.loads(SCHEMA.read_text(encoding="utf-8"))["dimensions"]
    labels = sorted({d["label"] for d in dims if d.get("label")})
    values = sorted({v for d in dims for v in (d.get("values") or [])})
    strings = labels + [v for v in values if v not in set(labels)]
    if args.limit:
        strings = strings[: args.limit]
    print("{} dimensions -> {} unique strings".format(len(dims), len(strings)))

    translated = translate(client, kwargs["model"], strings, args.batch_size)

    # Expand back per dimension. Omitting an untranslated key is deliberate:
    # the pack falls back to English at render time, which reads better than a
    # wrong translation.
    out: dict[str, dict] = {}
    for dimension in dims:
        entry: dict = {}
        label = translated.get(dimension.get("label") or "")
        if label:
            entry["label"] = label
        value_map = {
            value: translated[value]
            for value in (dimension.get("values") or [])
            if value in translated
        }
        if value_map:
            entry["values"] = value_map
        if entry:
            out[dimension["id"]] = entry

    target = SOURCES / args.locale
    target.mkdir(parents=True, exist_ok=True)
    (target / "meta.json").write_text(
        json.dumps({"reviewStatus": "machine-assisted"}, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "dimensions.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (target / "taxonomy.json").write_text(
        json.dumps(TAXONOMY_VI, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print("\nwrote {}".format(target))
    print("  strings translated : {}/{}".format(len(translated), len(strings)))
    print("  dimensions covered : {}/{}".format(len(out), len(dims)))
    print("\nnext: uv run python persona/schema/labels/build_labels.py --locale {}".format(args.locale))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
