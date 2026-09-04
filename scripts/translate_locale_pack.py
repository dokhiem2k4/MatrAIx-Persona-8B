#!/usr/bin/env python3
"""Machine-translate a UI message catalog, verifying ICU formatting survives.

The catalogs carry ICU message syntax -- ``{count}`` placeholders, ``<count>``
rich-text tags, and ``plural``/``select`` blocks. A translation that drops or
renames one of those does not fail loudly: ``intl-messageformat`` throws at
render time, so the damage shows up as a blank panel in whichever screen
happens to use that string. Every translation here is therefore checked to
carry exactly the same placeholder and tag multiset as its source, and anything
that fails is left untranslated so English shows through.

Matches the ``machine-assisted`` translationStatus the other packs declare.

Usage:
    uv run python scripts/translate_locale_pack.py \\
        --source .../messages/en-US.json --out .../messages/vi.json \\
        --language Vietnamese --locale vi
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "packages/playground/src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "packages/playground/src"))

# Variable names at any nesting depth: "{count, plural, one {#…} other {#…}}"
# yields "count". Matching on names rather than whole placeholder strings is
# what lets a language collapse plural branches -- Vietnamese has no plural
# inflection, so "one {# person} other {# people}" correctly becomes a single
# "other {# người}", which a literal comparison would reject as damage.
VARIABLE = re.compile(r"\{\s*([a-zA-Z_][a-zA-Z0-9_]*)")
TAG = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*>")
ICU_KEYWORD = re.compile(r"\b(plural|select|selectordinal)\b")
HASH = re.compile(r"#")

SYSTEM = """You translate UI strings for a developer tool into {language}.

Rules, in order of importance:
1. Preserve every {{placeholder}} EXACTLY -- same spelling, same braces. Never
   translate, reorder into a different placeholder, add, or drop one.
2. Preserve every <tag> and </tag> exactly as written.
3. ICU plural/select blocks keep their English keywords (plural, select, one,
   other, =0) -- translate only the human-readable text inside them.
4. Keep it short. These are buttons, labels and column headers in a dense UI;
   a translation noticeably longer than the source will break the layout.
5. Keep technical terms that developers read in English: persona, job, trial,
   token, prompt, schema, dataset, API, JSON, CSV.

Return ONLY a JSON object mapping each input key to its translation. No prose."""


def signature(text: str) -> tuple:
    """The formatting a translation must reproduce.

    Variable names and tags must match exactly -- a missing one throws at
    render time. Plural branch names deliberately do not, so a language with
    no plural inflection can collapse them; ICU only requires ``other``, and
    the ``#`` count marker must survive if the source had one.
    """
    return (
        tuple(sorted(VARIABLE.findall(text))),
        tuple(sorted(TAG.findall(text))),
        tuple(sorted(set(ICU_KEYWORD.findall(text)))),
        bool(HASH.search(text)),
    )


def translate_batch(client, model: str, language: str, batch: dict[str, str]) -> dict[str, str]:
    payload = json.dumps(batch, ensure_ascii=False, indent=None)
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM.format(language=language)},
            {"role": "user", "content": payload},
        ],
    )
    content = (response.choices[0].message.content or "").strip()
    if not content:
        return {}
    try:
        out = json.loads(content)
    except json.JSONDecodeError:
        return {}
    return out if isinstance(out, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--language", required=True, help="e.g. Vietnamese")
    parser.add_argument("--locale", required=True, help="e.g. vi")
    parser.add_argument("--batch-size", type=int, default=40)
    parser.add_argument("--limit", type=int, help="translate only the first N keys")
    parser.add_argument(
        "--model",
        default=os.environ.get("MATRIX_PERSONA_MODEL", "openrouter/google/gemini-3.5-flash-lite"),
    )
    args = parser.parse_args()

    from openai import OpenAI
    from playground.model_client import openrouter_openai_client_kwargs

    kwargs = openrouter_openai_client_kwargs(args.model)
    client = OpenAI(api_key=kwargs["api_key"], base_url=kwargs["base_url"])
    model = kwargs["model"]

    source = json.loads(args.source.read_text(encoding="utf-8"))
    keys = list(source)[: args.limit] if args.limit else list(source)

    # Resume: keep anything already translated and verified.
    out: dict[str, str] = {}
    if args.out.is_file():
        existing = json.loads(args.out.read_text(encoding="utf-8"))
        # Drop values identical to English: a previous run fills untranslated
        # keys with the source to keep key parity, and treating those as done
        # would permanently freeze them. Re-translating a genuinely identical
        # string costs one call; skipping a filled one loses it forever.
        out = {k: v for k, v in existing.items() if k in source and v != source[k]}
        if out:
            print("resuming with {} existing translations".format(len(out)))

    todo = [k for k in keys if k not in out]
    rejected: list[str] = []
    failed_batches = 0

    for start in range(0, len(todo), args.batch_size):
        chunk = todo[start : start + args.batch_size]
        batch = {k: source[k] for k in chunk}
        try:
            result = translate_batch(client, model, args.language, batch)
        except Exception as exc:  # noqa: BLE001 - one bad batch must not end the run
            print("  batch {} failed: {}".format(start, str(exc)[:90]))
            failed_batches += 1
            continue
        kept = 0
        for key in chunk:
            value = result.get(key)
            if not isinstance(value, str) or not value.strip():
                continue
            # The check that matters: same placeholders, tags and ICU keywords.
            if signature(value) != signature(source[key]):
                rejected.append(key)
                continue
            out[key] = value.strip()
            kept += 1
        print(
            "  {}/{} keys  (+{} this batch)".format(len(out), len(keys), kept),
            flush=True,
        )
        args.out.write_text(
            json.dumps(dict(sorted(out.items())), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    # packs.test.ts asserts exact key parity with English, so a pack that omits
    # a key fails the suite rather than quietly falling back. Fill the gaps with
    # the English source: same rendered result as the fallback, but the pack
    # stays complete and ICU-compilable.
    translated = len(out)
    for key in keys:
        out.setdefault(key, source[key])

    args.out.write_text(
        json.dumps(dict(sorted(out.items())), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("\nwrote {}".format(args.out))
    if len(out) > translated:
        print(
            "  filled {} untranslated key(s) with English to keep key parity".format(
                len(out) - translated
            )
        )
    print(
        "  translated : {}/{} ({:.0f}%)".format(
            translated, len(keys), translated / len(keys) * 100
        )
    )
    if rejected:
        print(
            "  rejected   : {} (formatting mismatch -- left in English)".format(len(rejected))
        )
        for key in rejected[:5]:
            print("      {}".format(key))
    if failed_batches:
        print("  failed batches: {}".format(failed_batches))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
