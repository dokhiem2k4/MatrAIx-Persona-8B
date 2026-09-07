"""Chatbot-flavored prompt adapter for post-conversation persona self-report."""

from __future__ import annotations

import json
from typing import Any, List

from playground.feedback import questionnaire_from_feedback
from playground.self_report_runtime import (
    SelfReportClient,
    complete_self_report_payload_with_usage,
    resolve_self_report_schema,
)
from playground.types import Persona, PlaygroundTurn, Questionnaire
from playground.user_sim.seed import ChatSeed
from playground.user_sim.self_report_contract import (
    SelfReportSchema,
    schema_prompt_block,
)

_FEEDBACK_USER = """You have now FINISHED using {chatbot_label}. Here is the full conversation \
and user-visible structured information from the interaction \
(you = user, {chatbot_label} = assistant):
{transcript}
{seed_block}
{instructions}

## How to rate
A rating nobody can trace back is worthless. Every explanation field must:
- Cite the turn number(s) it rests on, as "turn N" -- what was said or not said there.
- Name the thing about YOU that made you read it that way: your expectations,
  your situation while driving, how much patience you had. Two different people
  can watch the same reply and rate it differently; say what made yours yours.
- Follow from the conversation above, not from politeness. Use the whole range:
  rate it low when it let you down, high only when it genuinely earned that.

{schema_block}

Return strict JSON only with no prose before or after the JSON object."""

_SEED_BLOCK = """
## What you came in wanting
{situation}
Judge the assistant against THIS need -- did you leave with it handled?
"""


def _format_exposure_value(value: Any, *, kind: str) -> str:
    if kind == "item_list" and isinstance(value, list):
        parts = []
        for item in value:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or item.get("name") or "").strip()
            item_id = str(item.get("itemId") or item.get("id") or "").strip()
            if title and item_id:
                parts.append("{} ({})".format(title, item_id))
            elif title:
                parts.append(title)
            elif item_id:
                parts.append(item_id)
        return ", ".join(parts) or "[]"
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _format_transcript_turns(
    transcript: List[PlaygroundTurn],
    *,
    chatbot_label: str,
) -> str:
    lines: List[str] = []
    # Number the turns: an explanation can only cite evidence it can point at.
    for index, turn in enumerate(transcript, start=1):
        lines.append("turn {} | you: {}".format(index, turn.user_message))
        lines.append("turn {} | {}: {}".format(index, chatbot_label, turn.assistant_message))
        for item in turn.structured_exposure:
            label = str(item.get("label") or item.get("key") or "Visible detail")
            kind = str(item.get("format") or "text")
            value = _format_exposure_value(item.get("value"), kind=kind)
            if value.strip():
                lines.append("{} visible: {}".format(label, value))
    return "\n".join(lines) if lines else "(empty)"


def final_self_report(
    client: SelfReportClient,
    *,
    system_prompt: str,
    persona: Persona,
    transcript: List[PlaygroundTurn],
    schema: SelfReportSchema | None = None,
    chatbot_label: str = "Chatbot",
    seed: "ChatSeed | None" = None,
) -> Questionnaire:
    questionnaire, _usage = final_self_report_with_usage(
        client,
        system_prompt=system_prompt,
        persona=persona,
        transcript=transcript,
        schema=schema,
        chatbot_label=chatbot_label,
        seed=seed,
    )
    return questionnaire


def final_self_report_with_usage(
    client: SelfReportClient,
    *,
    system_prompt: str,
    persona: Persona,
    transcript: List[PlaygroundTurn],
    schema: SelfReportSchema | None = None,
    chatbot_label: str = "Chatbot",
    seed: "ChatSeed | None" = None,
) -> tuple[Questionnaire, Any]:
    del persona
    schema = resolve_self_report_schema(schema)
    situation = "\n".join(seed.situation_lines()) if seed is not None else ""
    user = _FEEDBACK_USER.format(
        chatbot_label=chatbot_label,
        transcript=_format_transcript_turns(transcript, chatbot_label=chatbot_label),
        seed_block=_SEED_BLOCK.format(situation=situation) if situation else "",
        instructions=schema.instructions
        or "Reflect honestly from your own point of view as this persona.",
        schema_block=schema_prompt_block(schema),
    )
    payload, usage = complete_self_report_payload_with_usage(
        client,
        system_prompt=system_prompt,
        user_prompt=user,
        schema=schema,
    )
    return questionnaire_from_feedback(payload), usage
