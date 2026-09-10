#!/usr/bin/env python3
"""Keep a persona's name consistent with the register it was measured to use.

A vn-driver persona is two people: driving answers from a questionnaire
respondent, demographics from a WVS respondent, paired at random because the
two layers share no dimension to stratify on. The pairing is a stated
limitation of ``merge_persona_layers.py`` and it usually stays out of sight,
because ``gender_identity`` is guard tier and never rendered.

The name is rendered. So a driver who answered that she calls herself "chị"
can be handed a man's demographics, a man's name, and a prompt that opens "You
are <man's name>" and then instructs her to say "chị". Only the display name
leaks the contradiction, and only the display name is safe to change: it is
generated from ``vn_names``, so aligning it edits nothing anyone answered.

Five of the seven registers state no gender, and those personas are left alone
-- there is nothing to be inconsistent with.

    uv run python scripts/align_persona_names_to_register.py <pool>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "persona/curation/existing_data/scripts"))
sys.path.insert(0, str(REPO_ROOT))

from crosswalks.vn_drivers import gender_stated_by_register  # noqa: E402

from matraix.persona_pool import persona_paths  # noqa: E402

from persona.human_extraction.vn_names import vietnamese_name  # noqa: E402

MEASURED_TYPES = {"observed", "direct", "forum_measured"}


def needs_realignment(persona: dict) -> str | None:
    """The gender the register states, when the name does not already match.

    Returns None when the register states no gender, when it was not measured,
    or when the persona already agrees with it.
    """
    dims = persona.get("dimensions") or {}
    grounding = persona.get("grounding") or {}
    register = dims.get("vn_address_register")
    if not register:
        return None
    entry = grounding.get("vn_address_register") or {}
    if str(entry.get("assignment_type")) not in MEASURED_TYPES:
        return None
    stated = gender_stated_by_register(str(register))
    if stated is None or stated == dims.get("gender_identity"):
        return None
    return stated


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pool", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    changed = []
    for path in persona_paths(args.pool):
        persona = yaml.safe_load(path.read_text(encoding="utf-8"))
        stated = needs_realignment(persona)
        if stated is None:
            continue
        before = persona.get("display_name")
        # Deterministic in the persona id, so the surname survives and only
        # the given name moves: the same person, named consistently.
        persona["display_name"] = vietnamese_name(persona["persona_id"], stated)
        # The demographics still belong to the WVS respondent; only the name
        # was ever ours to choose, and the record says which is which.
        persona.setdefault("grounding", {}).setdefault("display_name", {}).update(
            {
                "assignment_type": "generated",
                "source_ref": "vn_names",
                "evidence": "aligned to measured vn_address_register={}".format(
                    persona["dimensions"]["vn_address_register"]
                ),
            }
        )
        changed.append((persona["persona_id"], before, persona["display_name"], stated))
        if not args.dry_run:
            path.write_text(
                yaml.safe_dump(
                    persona, allow_unicode=True, sort_keys=False, width=1000
                ),
                encoding="utf-8",
            )

    print(f"{len(changed)} persona(s) renamed to match a measured register")
    for pid, before, after, stated in changed:
        print(f"  {pid}: {before} -> {after}  ({stated})")
    if args.dry_run:
        print("(dry run -- nothing written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
