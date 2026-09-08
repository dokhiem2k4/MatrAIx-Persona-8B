import { describe, expect, it } from "vitest";

import { newFacetsIn } from "../ChatTrialDebrief";
import type { TrialEvaluationContext } from "@/lib/types";

function context(
  contextType: string,
  facets: Array<Partial<TrialEvaluationContext["facets"][number]>>,
): TrialEvaluationContext {
  return {
    key: `${contextType}.primary`,
    label: contextType,
    contextType,
    facets: facets.map((facet) => ({
      key: "k",
      label: "l",
      kind: "categorical",
      ...facet,
    })) as TrialEvaluationContext["facets"],
  };
}

const keys = (context: TrialEvaluationContext, present: string[] = []) =>
  newFacetsIn(context, new Set(present), new Set()).map((facet) => facet.key);

describe("evaluation detail filter", () => {
  it("drops facets the summary cards already show whole", () => {
    const block = context("task_outcome", [
      { key: "outcome_status", value: "unresolved" },
      { key: "resolution_basis", value: "verifier_scoring" },
      { key: "decision_correct", value: "no" },
    ]);
    expect(keys(block)).toEqual(["decision_correct"]);
  });

  it("keeps two answers that happen to share a word", () => {
    // The bug this guards: deduplicating every string, not just prose, made
    // "tool calls correct: no" vanish because "decision correct: no" came
    // first -- so the page silently lost a verdict.
    const block = context("task_outcome", [
      { key: "decision_correct", value: "no" },
      { key: "tool_calls_correct", value: "no" },
      { key: "case_integrity_ok", value: "not_applicable" },
    ]);
    expect(keys(block)).toEqual([
      "decision_correct",
      "tool_calls_correct",
      "case_integrity_ok",
    ]);
  });

  it("drops a coded verdict when the plain one is present", () => {
    const block = context("error_recovery", [
      { key: "decision_match", value: "mismatch", role: "primary" },
      { key: "tool_call_match", value: "mismatch", role: "primary" },
      { key: "observed_tools", value: "open_google_maps_route", role: "evidence" },
      { key: "expected_decision", value: "defer_retry", role: "evidence" },
    ]);
    const present = ["decision_correct", "tool_calls_correct", "tool_call_report"];
    expect(keys(block, present)).toEqual(["expected_decision"]);
  });

  it("keeps the coded verdict when nothing supersedes it", () => {
    const block = context("error_recovery", [
      { key: "decision_match", value: "mismatch", role: "primary" },
    ]);
    expect(keys(block)).toEqual(["decision_match"]);
  });

  it("drops report-slicing metadata", () => {
    const block = context("error_recovery", [
      { key: "case_id", value: "vg_0069", role: "control" },
      { key: "error_type", value: "no_internet", role: "control" },
      { key: "sut_intent", value: "navigation", role: "evidence" },
    ]);
    expect(keys(block)).toEqual(["sut_intent"]);
  });

  it("drops prose the card showed almost all of, keeps what it cut", () => {
    const short = "x".repeat(200); // card shows 140 of it -> not worth repeating
    const long = "y".repeat(400); // card shows 140 -> most of it is unread
    const block = context("conversation_summary", [
      { key: "process_notes", value: short, kind: "textual" },
      { key: "conversation_path", value: long, kind: "textual" },
    ]);
    expect(keys(block)).toEqual(["conversation_path"]);
  });

  it("shows a paragraph only once across contexts", () => {
    // outcome_reason and feedback_reason are the same text whenever the
    // verdict was derived from the persona's own words.
    const shared = "z".repeat(400);
    const seen = new Set<string>();
    const present = new Set<string>();
    const first = newFacetsIn(
      context("task_outcome", [
        { key: "outcome_reason", value: shared, kind: "textual" },
      ]),
      present,
      seen,
    );
    const second = newFacetsIn(
      context("user_feedback", [
        { key: "feedback_reason", value: shared, kind: "textual" },
      ]),
      present,
      seen,
    );
    expect(first).toHaveLength(1);
    expect(second).toHaveLength(0);
  });

  it("drops blank facets", () => {
    const block = context("user_feedback", [
      { key: "clarifying_notes", value: "", kind: "textual" },
      { key: "personal_preference_satisfaction", value: "partially" },
    ]);
    expect(keys(block)).toEqual(["personal_preference_satisfaction"]);
  });
});
