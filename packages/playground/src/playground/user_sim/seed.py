"""Per-trial conversation seed: the stimulus row a multi-turn trial replays.

Stage-1 utterance surveys emit ``scenario`` + ``first_input`` pairs (see
``scripts/export_vita_utterances.py``); stage-2 replays one row as one
multi-turn conversation. Without a seed the persona invents its own need, so
two runs are never comparable -- the seed is what anchors a run to a fixed
stimulus set.

The row rides on ``agents[].kwargs`` -- the same channel that already carries
per-trial ``persona_path``. Note that ``agents[].env`` does NOT work here:
``AgentFactory`` hands it to the agent as ``extra_env``, but only subprocess
CLI agents (``InstalledAgent``) keep it; ``BaseAgent`` -- which the host-native
``PersonaUserSim`` extends -- accepts and discards it, so a seed sent that way
would silently never arrive.

``MATRIX_CHATBOT_SEED`` stays available as a fallback for driving a one-off run
by hand, but the job config is the real channel.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Mapping, Optional

SEED_ENV_VAR = "MATRIX_CHATBOT_SEED"


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


@dataclass(frozen=True)
class ChatSeed:
    """One dataset row bound to one multi-turn trial."""

    scenario: str = ""
    first_input: str = ""
    row_id: str = ""
    intent_code: str = ""
    subintent_code: str = ""
    subintent_name: str = ""
    vehicle_state: str = ""
    assistant_mode: str = ""
    source_persona_id: str = ""

    def is_empty(self) -> bool:
        """True when there is nothing to anchor on."""
        return not self.scenario and not self.first_input

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "ChatSeed":
        return cls(
            scenario=_text(payload.get("scenario")),
            first_input=_text(payload.get("first_input")),
            row_id=_text(payload.get("row_id")),
            intent_code=_text(payload.get("intent_code")),
            subintent_code=_text(payload.get("subintent_code")),
            subintent_name=_text(payload.get("subintent_name")),
            vehicle_state=_text(payload.get("vehicle_state")),
            # The workbook column is upper-case; accept both spellings so the
            # dataset can be forwarded without renaming.
            assistant_mode=_text(
                payload.get("assistant_mode") or payload.get("ASSISTANT_MODE")
            ),
            source_persona_id=_text(
                payload.get("source_persona_id") or payload.get("persona_id")
            ),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "rowId": self.row_id,
            "scenario": self.scenario,
            "firstInput": self.first_input,
            "intentCode": self.intent_code,
            "subintentCode": self.subintent_code,
            "subintentName": self.subintent_name,
            "vehicleState": self.vehicle_state,
            "assistantMode": self.assistant_mode,
            "sourcePersonaId": self.source_persona_id,
        }

    def situation_lines(self) -> list[str]:
        """Human-readable situation facts, shared by kickoff and self-report."""
        lines: list[str] = []
        if self.scenario:
            lines.append("Situation: {}".format(self.scenario))
        if self.vehicle_state:
            lines.append("Vehicle state: {}".format(self.vehicle_state))
        if self.assistant_mode:
            lines.append("Assistant mode: {}".format(self.assistant_mode))
        return lines

    def kickoff_text(self) -> str:
        """Replace the free-invention kickoff with this row's specific need.

        The persona rephrases rather than replays ``first_input`` verbatim, so
        the opening turn keeps the persona's own voice while every run of this
        row still opens on the same underlying need.
        """
        parts = list(self.situation_lines())
        if self.first_input:
            parts.append(
                "What you want from the assistant, in substance: {}".format(
                    self.first_input
                )
            )
        parts.append(
            "Open the conversation with THIS need, phrased in your own words -- "
            "do not copy the sentence above verbatim, and do not substitute a "
            "different goal. After the opening turn, behave like a genuine "
            "human user: reveal details gradually, react to what the assistant "
            "says, push back when it misses, and keep messages short (1-3 "
            "sentences)."
        )
        return "\n".join(parts)


def resolve_chat_seed(
    payload: Any = None,
    *,
    environ: Optional[Mapping[str, str]] = None,
) -> Optional[ChatSeed]:
    """Seed for this trial: the job config's row, else the env fallback.

    ``payload`` arrives from ``agents[].kwargs`` and may be a mapping, an
    already-built :class:`ChatSeed`, or a JSON string (YAML authors sometimes
    quote it). Anything unusable falls through to the env var.
    """
    if isinstance(payload, ChatSeed):
        return None if payload.is_empty() else payload
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except (TypeError, ValueError):
            payload = None
    if isinstance(payload, Mapping):
        seed = ChatSeed.from_mapping(payload)
        if not seed.is_empty():
            return seed
    return chat_seed_from_env(environ)


def chat_seed_from_env(environ: Optional[Mapping[str, str]] = None) -> Optional[ChatSeed]:
    """Load the trial's seed, or ``None`` when the run is unseeded.

    A malformed value is treated as absent: an unseeded conversation is still a
    valid run, so a bad env var must not take the whole trial down.
    """
    source = os.environ if environ is None else environ
    raw = (source.get(SEED_ENV_VAR) or "").strip()
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(payload, Mapping):
        return None
    seed = ChatSeed.from_mapping(payload)
    return None if seed.is_empty() else seed
