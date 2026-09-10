"""Jinja2 rendering for persona prompt templates."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound

from matraix.agents.persona.loader import Persona
from matraix.persona_dimension_catalog import build_template_context_extras
from matraix.persona_tiers import (
    label_overrides,
    prompt_tier_dimensions,
    stamped_tiers,
)

PERSONA_SYSTEM_TEMPLATE = "persona_system.md.j2"
PERSONA_INSTRUCTION_TEMPLATE = "persona_instruction.md.j2"


def default_templates_dir() -> Path:
    """Bundled persona prompt templates (Environment runtime, not persona data)."""
    return Path(__file__).resolve().parent / "templates"


def resolve_persona_template(
    persona: Persona,
    template_path: str | Path | None,
    default_name: str,
) -> Path:
    if template_path is not None:
        candidate = Path(template_path).expanduser()
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        resolved = candidate.resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"Persona template not found: {template_path}")
        return resolved

    default = default_templates_dir() / default_name
    if not default.is_file():
        raise FileNotFoundError(
            f"Default persona template not found: {default}. "
            "Pass persona_template_path=... to override."
        )
    return default.resolve()


def render_persona_template(
    template_path: Path,
    persona: Persona,
    *,
    instruction: str | None = None,
) -> str:
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    try:
        template = env.get_template(template_path.name)
    except TemplateNotFound as exc:
        raise FileNotFoundError(f"Persona template not found: {template_path}") from exc

    # The record carries every field it was built from; only the prompt tier is
    # meant to reach the model. No job config points at the rendered view, so
    # filtering here is the only place the tier is honoured at all.
    return template.render(
        **persona.template_context(instruction=instruction),
        **build_template_context_extras(
            prompt_tier_dimensions(persona.data),
            label_overrides=label_overrides(persona.data),
            # A tiered pool already chose these fields, so a value sitting on
            # its schema default is still information and must not be elided.
            tiered=bool(stamped_tiers(persona.data)),
        ),
    ).strip()
