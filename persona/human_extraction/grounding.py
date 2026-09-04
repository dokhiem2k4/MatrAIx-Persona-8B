"""Per-dimension provenance for persona YAML files.

A persona YAML carries one top-level ``source`` ("wiki", "gss", "synthetic")
for the whole file, so once several sources are combined -- WVS demographics,
forum-measured language, a driver questionnaire -- there is no way to tell which
dimension came from where. The parquet release has a ``grounding`` column for
exactly this; the YAML that actually feeds the persona agent does not.

This adds a ``grounding`` block keyed by dimension id, mirroring the parquet
struct (evidence / confidence / assignment_type) plus the source id, so a
finished result can be filtered down to only what was measured.

    grounding:
      age_bracket:
        assignment_type: observed
        source_ref: wvs_wave7_vnm
        evidence: "B_COUNTRY_ALPHA=VNM row 417; Q262"
        confidence: 1.0

Assignment types are ordered by how much weight a reading can carry. Only the
first three may be used to score a run; ``summary_inference`` is kept as data
but excluded, matching the ConvAI2 extraction, which dropped its source's
``domain`` and ``seniority_level`` columns precisely because they were upstream
inferences.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping

# Ordered strongest to weakest.
OBSERVED = "observed"  # a real respondent answered this question
DIRECT = "direct"  # an explicit statement, deterministically matched
FORUM_MEASURED = "forum_measured"  # measured from the person's own writing
SUMMARY_INFERENCE = "summary_inference"  # inferred from tone/context
GENERATED = "generated"  # sampled from the synthesis graph
UNSUPPORTED = "unsupported"  # no evidence; the value is null

ASSIGNMENT_TYPES = (
    OBSERVED,
    DIRECT,
    FORUM_MEASURED,
    SUMMARY_INFERENCE,
    GENERATED,
    UNSUPPORTED,
)

#: Types a dimension may carry and still be used to score a benchmark run.
SCOREABLE = frozenset({OBSERVED, DIRECT, FORUM_MEASURED})


class GroundingError(ValueError):
    """Raised when a grounding record cannot be trusted as written."""


@dataclass(frozen=True)
class Grounding:
    """Where one dimension's value came from."""

    assignment_type: str
    source_ref: str = ""
    evidence: str = ""
    confidence: float | None = None

    def __post_init__(self) -> None:
        if self.assignment_type not in ASSIGNMENT_TYPES:
            raise GroundingError(
                "unknown assignment_type {!r}; expected one of {}".format(
                    self.assignment_type, ", ".join(ASSIGNMENT_TYPES)
                )
            )
        # Evidence is what makes a claim checkable later. Demanding it only for
        # the scoreable types keeps generated values cheap to record.
        if self.assignment_type in SCOREABLE and not (self.source_ref or self.evidence):
            raise GroundingError(
                "{} requires source_ref or evidence -- an unsourced measurement "
                "cannot be verified later".format(self.assignment_type)
            )
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise GroundingError(
                "confidence {} outside 0..1".format(self.confidence)
            )

    @property
    def scoreable(self) -> bool:
        return self.assignment_type in SCOREABLE

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v not in (None, "")}

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "Grounding":
        raw = payload.get("confidence")
        return cls(
            assignment_type=str(payload.get("assignment_type") or UNSUPPORTED),
            source_ref=str(payload.get("source_ref") or ""),
            evidence=str(payload.get("evidence") or ""),
            confidence=float(raw) if raw is not None else None,
        )


@dataclass
class GroundedPersona:
    """A persona plus the provenance of every dimension it carries."""

    persona_id: str
    display_name: str
    dimensions: dict[str, Any] = field(default_factory=dict)
    grounding: dict[str, Grounding] = field(default_factory=dict)
    source: str = ""
    version: str = "1.0"

    def set(
        self,
        dimension: str,
        value: Any,
        *,
        assignment_type: str,
        source_ref: str = "",
        evidence: str = "",
        confidence: float | None = None,
    ) -> None:
        """Record a value together with where it came from.

        A null value is recorded as unsupported rather than dropped, so a later
        reader can tell "nobody asked" apart from "asked, no answer".
        """
        if value is None or str(value).strip() == "":
            self.dimensions.pop(dimension, None)
            self.grounding[dimension] = Grounding(UNSUPPORTED)
            return
        self.dimensions[dimension] = value
        self.grounding[dimension] = Grounding(
            assignment_type=assignment_type,
            source_ref=source_ref,
            evidence=evidence,
            confidence=confidence,
        )

    def scoreable_dimensions(self) -> list[str]:
        return sorted(d for d, g in self.grounding.items() if g.scoreable and d in self.dimensions)

    def counts_by_type(self) -> dict[str, int]:
        counts = {t: 0 for t in ASSIGNMENT_TYPES}
        for g in self.grounding.values():
            counts[g.assignment_type] += 1
        return {t: c for t, c in counts.items() if c}

    def sources(self) -> list[str]:
        return sorted({g.source_ref for g in self.grounding.values() if g.source_ref})

    def to_yaml_dict(self) -> dict[str, Any]:
        """Payload for the persona YAML. `grounding` sits beside `dimensions`."""
        return {
            "persona_id": self.persona_id,
            "version": self.version,
            "source": self.source or "+".join(self.sources()) or "unknown",
            "display_name": self.display_name,
            "dimensions": dict(sorted(self.dimensions.items())),
            "grounding": {
                d: g.to_dict() for d, g in sorted(self.grounding.items())
            },
            "grounding_summary": {
                "scoreable": len(self.scoreable_dimensions()),
                "byAssignmentType": self.counts_by_type(),
                "sources": self.sources(),
            },
        }

    @classmethod
    def from_yaml_dict(cls, payload: Mapping[str, Any]) -> "GroundedPersona":
        return cls(
            persona_id=str(payload.get("persona_id") or ""),
            display_name=str(payload.get("display_name") or ""),
            dimensions=dict(payload.get("dimensions") or {}),
            grounding={
                str(d): Grounding.from_mapping(g)
                for d, g in (payload.get("grounding") or {}).items()
                if isinstance(g, Mapping)
            },
            source=str(payload.get("source") or ""),
            version=str(payload.get("version") or "1.0"),
        )


def ungrounded_dimensions(persona: GroundedPersona) -> list[str]:
    """Dimensions carrying a value with no provenance recorded at all.

    These are the dangerous ones: they look identical to measured values in the
    prompt, and nothing downstream can tell them apart.
    """
    return sorted(d for d in persona.dimensions if d not in persona.grounding)


def summarise(personas: Iterable[GroundedPersona]) -> dict[str, Any]:
    """Batch view: how much of this cohort rests on measurement."""
    personas = list(personas)
    if not personas:
        return {"personas": 0}
    scoreable = [len(p.scoreable_dimensions()) for p in personas]
    totals: dict[str, int] = {}
    sources: set[str] = set()
    for p in personas:
        for t, c in p.counts_by_type().items():
            totals[t] = totals.get(t, 0) + c
        sources.update(p.sources())
    return {
        "personas": len(personas),
        "scoreableMean": round(sum(scoreable) / len(scoreable), 2),
        "scoreableMin": min(scoreable),
        "scoreableMax": max(scoreable),
        "byAssignmentType": dict(sorted(totals.items(), key=lambda kv: -kv[1])),
        "sources": sorted(sources),
    }
